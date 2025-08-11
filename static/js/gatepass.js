document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('.gatepass-form');
  const submitBtn = document.getElementById('gatepass-submit-btn');

  if (form && submitBtn) {
    form.addEventListener('submit', function(e) {
      submitBtn.disabled = true;
      submitBtn.innerText = 'Submitting...';
    });
  }
}); 