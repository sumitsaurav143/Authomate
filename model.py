from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class KYCSubmission(Base):
    __tablename__ = "kyc_submissions"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    id_no = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    confirm_password = Column(String, nullable=True)
    filename = Column(String)
    extracted_text = Column(Text)
    flags = Column(Text)
    kycVerified = Column(Integer, default=0) 
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)