
const fileInput = document.getElementById('idFile');
const preview = document.getElementById('preview');
const toast = document.getElementById('toast');
const progressBar = document.getElementById('progressBar');
const progressBarContainer = document.getElementById('progressBarContainer');

fileInput.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
});

function showToast(message, isError = false) {
    toast.textContent = message;
    toast.classList.add('show');
    if (isError) toast.classList.add('error');
    else toast.classList.remove('error');

    setTimeout(() => {
        toast.classList.remove('show');
        // Redirect on success
        if (!isError) {
            window.location.href = "verification-result.html";
        }
    }, 1500);
}

async function submitFile() {
    console.log("submitFile() called");
    const file = fileInput.files[0];
    if (!file) {
        showToast("Please choose a file first!", true);
        return;
    }

    // Get userData from localStorage and parse it
    const userData = JSON.parse(sessionStorage.getItem("currentUser"));
    if (!userData) {
        showToast("User data not found!", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("full_name", userData.full_name);
    formData.append("dob", userData.dob);
    formData.append("id_no", userData.id_no);
    formData.append("email", userData.email);
    formData.append("password", userData.password);
    formData.append("confirm_password", userData.confirm_password);

    progressBarContainer.classList.remove('hidden');
    progressBar.style.width = '0%';

    try {
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress >= 100) {
                clearInterval(progressInterval);
            } else {
                progress += 20;
                progressBar.style.width = progress + "%";
            }
        }, 150);

        // Real API call
        const response = await fetch("http://127.0.0.1:8000/kyc/verify", {
            method: "POST",
            body: formData
        });
        

        console.log("formData:", formData);
        console.log("Response status:", response);

        if (!response.ok) {
            throw new Error("Upload failed!");
        }

        const result = await response.json();

        sessionStorage.setItem("kycResult", JSON.stringify(result));
        window.location.href = "verification-result.html";

    } catch (error) {
        console.error(error);
        showToast("Upload failed!", true);
    }
}
