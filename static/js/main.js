


function togglePassword(fieldId) {                                                                                         /*  Toggle password visibility  */
  const field = document.getElementById(fieldId);
  const eye   = document.getElementById(`eye-${fieldId}`);
  if (!field) return;
  if (field.type === 'password') {
    field.type = 'text';
    eye && eye.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
    field.type = 'password';
    eye && eye.classList.replace('fa-eye-slash', 'fa-eye');
  }
}

 
function previewAvatar(event) {                                                                                                  /*  Profile picture preview  */
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const preview = document.getElementById('avatarPreview');
    if (preview) {
      preview.innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:50%">`;
    }
  };
  reader.readAsDataURL(file);
}


const pwInput = document.getElementById('password');                                                                                      /* Password strength indicator */
if (pwInput) {
  pwInput.addEventListener('input', () => {
    const val = pwInput.value;
    const wrap = pwInput.closest('.input-group');
    wrap.classList.remove('ps-weak', 'ps-medium', 'ps-strong');
    if (val.length === 0) return;
    const strong = /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d]).{8,}/.test(val);
    const medium = /(?=.*[a-zA-Z])(?=.*\d).{6,}/.test(val);
    if (strong)       wrap.classList.add('ps-strong');
    else if (medium)  wrap.classList.add('ps-medium');
    else              wrap.classList.add('ps-weak');
  });
}


function toggleSidebar() {                                                                                                             /*  Sidebar toggle  */
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('mobile-open');
  } else {
    sidebar.classList.toggle('collapsed');
    const main = document.querySelector('.main-content');
    if (main) main.style.marginLeft = sidebar.classList.contains('collapsed') ? '64px' : '';
  }
}


function openModal(id) {                                                                                                /*  Modal helpers  */
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}
function closeModalOutside(event, id) {
  if (event.target === event.currentTarget) closeModal(id);
}


document.addEventListener('DOMContentLoaded', () => {                                                                 /*  Auto-dismiss toasts after 4s  */
  document.querySelectorAll('.toast').forEach(t => {
    setTimeout(() => t.remove(), 4000);
  });
});

/*  Close sidebar on outside click   */
document.addEventListener('click', e => {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  if (window.innerWidth <= 768 && sidebar.classList.contains('mobile-open')) {
    if (!sidebar.contains(e.target) && !e.target.closest('.menu-btn')) {
      sidebar.classList.remove('mobile-open');
    }
  }
});
