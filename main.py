from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from PIL import Image
from datetime import datetime
from database import SessionLocal, init_db
from sqlalchemy.orm import Session
from model import KYCSubmission
from fastapi import Depends
import json
import numpy as np
import cv2
import re
import io
import easyocr


reader = easyocr.Reader(['en'], gpu=True)

app = FastAPI(title="KYC Compliance API")
init_db() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # only this origin is allowed
    allow_credentials=True,  # only needed if you're using cookies/auth headers
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_dob(dob_str):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(dob_str, fmt).date()
        except ValueError:
            continue
    return None

def preprocess_image(pil_image):
    image = np.array(pil_image.convert('RGB'))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def clean_text(text):
    return re.sub(r'[^a-z0-9\s:/-]', '', text.lower())

@app.post("/kyc/verify")
async def verify_kyc(
    file: UploadFile = File(...),
    full_name: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    id_no: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    confirm_password: Optional[str] = Form(None)

):
    try:
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents))

        # OCR processing
        processed = preprocess_image(pil_image)
        results = reader.readtext(processed, detail=0, paragraph=True)
        extracted_text = "\n".join(results)
        #extracted_text = pytesseract.image_to_string(processed, config="--oem 3 --psm 6")
        text_norm = clean_text(extracted_text)

        compliance_report = []
        kycFailedFlag = False
        flags = {
            "DOCUMENT_NOT_EXPIRED": True,
            "CLEAR_DOCUMENT": True,
            "NAME_MATCHED": False,
            "DOB_MATCHED": False,
            #"dob_format_invalid": False,
            "ID_NO_MATCHED": False
        }

        if "expired" in text_norm:
            flags["DOCUMENT_NOT_EXPIRED"] = False
            kycFailedFlag = True

        if len(extracted_text.strip()) < 30:
            flags["CLEAR_DOCUMENT"] = False
            kycFailedFlag = True

        if full_name:
            if clean_text(full_name) in text_norm:
                flags["NAME_MATCHED"] = True
                compliance_report.append(f"✅ Name '{full_name}' matched.")
            else:
                flags["NAME_MATCHED"] = False
                kycFailedFlag = True
                compliance_report.append(f"❌ Name '{full_name}' NOT matched.")

        if id_no:
            if clean_text(id_no) in text_norm:
                flags["ID_NO_MATCHED"] = True
                compliance_report.append(f"✅ ID Number '{id_no}' matched.")
            else:
                flags["ID_NO_MATCHED"] = False
                kycFailedFlag = True
                compliance_report.append(f"❌ ID Number '{id_no}' NOT matched.")

        if dob:
            dob_date = parse_dob(dob)
            if dob_date:
                dob_formats = [dob_date.strftime("%Y-%m-%d"), dob_date.strftime("%d/%m/%Y")]
                if any(d in text_norm for d in dob_formats):
                    flags["DOB_MATCHED"] = True
                    compliance_report.append(f"✅ Date of Birth '{dob}' matched.")
                else:
                    flags["DOB_MATCHED"] = False
                    kycFailedFlag = True
                    compliance_report.append(f"❌ Date of Birth '{dob}' NOT matched.")
            else:
                #flags["dob_format_invalid"] = True
                kycFailedFlag = True
                compliance_report.append("⚠️ Date of Birth format should be YYYY-MM-DD or DD/MM/YYYY.")

        # Save to DB
        db = SessionLocal()
        existing_user = db.query(KYCSubmission).filter(KYCSubmission.email == email).first()
        if existing_user:
            db.close()
            return JSONResponse(
                status_code=400,
                content={"error": f"User with email '{email}' is already registered."}
            )

        kyc_entry = KYCSubmission(
            full_name=full_name,
            dob=dob,
            id_no=id_no,
            email=email,
            password=password, 
            filename=file.filename,
            extracted_text=extracted_text,
            flags=json.dumps(flags),
            kycVerified=not kycFailedFlag
        )
        db.add(kyc_entry)
        db.commit()
        db.refresh(kyc_entry)
        db.close()

        return JSONResponse({
            #"extracted_text": extracted_text,
            "compliance_report": compliance_report,
            "flags": flags,
            "kycVerified":not kycFailedFlag
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    return JSONResponse(content={
        "API Status": "Running"
    })


@app.get("/userData")
def get_kyc_submissions(email: Optional[str] = None, db: Session = Depends(get_db)):
    if email:
        submissions = db.query(KYCSubmission).filter(KYCSubmission.email == email).all()
    else:
        submissions = db.query(KYCSubmission).all()

    result = []
    for sub in submissions:
        result.append({
            "id": sub.id,
            "full_name": sub.full_name,
            "dob": sub.dob,
            "id_no": sub.id_no,
            "email": sub.email, 
            "password": sub.password,
            "filename": sub.filename,
            "extracted_text": sub.extracted_text,
            "flags": json.loads(sub.flags),
            "kycVerified": sub.kycVerified,
            "upload_time": sub.upload_time.isoformat()
        })
    return result