document.addEventListener('DOMContentLoaded', function() {
    // Display user info from session storage
    const userData = JSON.parse(sessionStorage.getItem('currentUser'));
    if (!userData) {
        window.location.href = 'register.html';
        return;
    }

    document.getElementById('userInfo').innerHTML = `
        <p><strong>Name:</strong> ${userData.fullName}</p>
        <p><strong>Email:</strong> ${userData.email}</p>
    `;

    // Handle verification form submission
    document.getElementById('verificationForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const idType = document.getElementById('idType').value;
        const idNumber = document.getElementById('idNumber').value;
        const idPhoto = document.getElementById('idPhoto').files[0];
        const selfie = document.getElementById('selfie').files[0];
        
        // Store verification data
        const verificationData = {
            idType,
            idNumber,
            idPhotoName: idPhoto.name,
            selfieName: selfie.name,
            submittedAt: new Date().toISOString()
        };
        
        // Update user data
        userData.verification = verificationData;
        sessionStorage.setItem('currentUser', JSON.stringify(userData));
        
        // Redirect to verification result page
        window.location.href = 'verification-result.html';
    });
});