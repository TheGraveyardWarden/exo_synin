let signin_btn = document.getElementsByName('signin_btn')[0];
let user_inp = document.getElementsByName('username')[0];
let pass_inp = document.getElementsByName('password')[0];
let loading = document.getElementsByName('loading')[0];
let alerts = document.querySelectorAll('.alert');

if(alerts) {
    alerts.forEach((a, i) => {
        setTimeout(() => {
            a.style.display = 'none';
        }, 5000)
    })
}

signin_btn.addEventListener('click', () => {
    loading.classList.remove('visually-hidden');
    if(!(user_inp.value)) {
        user_inp.classList.remove('m_inp_border');
        user_inp.classList.add('is-invalid');
    } else {
        user_inp.classList.add('m_inp_border');
        user_inp.classList.remove('is-invalid');
    }
    if(!(pass_inp.value)) {
        pass_inp.classList.remove('m_inp_border');
        pass_inp.classList.add('is-invalid');
    } else {
        pass_inp.classList.add('m_inp_border');
        pass_inp.classList.remove('is-invalid');
    }
})