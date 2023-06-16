let send_btn = document.querySelector('.send_btn');
let text_inp = document.querySelector('.m_text_inp');
let chats = document.querySelector('.m_chats');
let create_chat_username = document.getElementsByName('create_chat_username')[0];
let create_chat_btn = document.getElementsByName('create_chat_btn')[0];
let create_chat_message = document.getElementsByName('create_chat_message')[0];
let chat_box_con = document.querySelector('.m_chat_box_con');
let create_group_btn = document.getElementsByName('create_group_btn')[0];

let toasts = [];

const is_chat_box_there = username => {
    let els = document.querySelectorAll('.m_chat_name');
    for(let i = 0; i < els.length; i++) {
        if(els[i].innerHTML === username) return true;
    }
    return false;
}

const create_chat_box = (avatar, username, last_msg, type = 'pv') => {
    if(is_chat_box_there(username)) {
        return;
    }
    chat_box_con.innerHTML += `
        <div data-type=${type} class="m_flex_row_spcbtw m_chat_box full_width mb-3 m_pointer">
             <div class="m_flex_row_start">
                <img alt="his_profile" src="http://5.75.196.210:8888/files/get-user-avatar/${avatar}" class="profile_pic" />
                <div class="m_flex_col_start m_align_def m_chat_box_info">
                    <p class="m_chat_name">${username}</p>
                    <p class="m_chat_last_msg">${last_msg}</p>
                </div>
            </div>
            <div class="m_flex_col_start m_align_end">
                <p class="m_text_muted m_chat_box_date" style="margin-bottom: 5px!important;">15 min ago</p>
                <div class="m_notif_number m_chat_box_notif" style="display: none;">0</div>
            </div>
        </div>`;
    handle_select('.m_chat_box', 'm_chat_box_selected', -99);
    handle_chats();
}

create_chat_btn.addEventListener('click', () => {
    if(create_chat_username.value && create_chat_message.value) {
        document.getElementsByName('new_chat_popup')[0].classList.add('visually-hidden');
        // if(is_chat_box_there(create_chat_username.value)) find_chat_box(create_chat_username.value).click();
        socket.emit('create_pv', create_chat_message.value, create_chat_username.value, res => {
            const {success, avatar, message, receiver} = res;
            if(success) {
                const {text, _id} = message;
                create_chat_box(avatar, receiver, text);
                setTimeout(() => find_chat_box(receiver).click(), 500);
                // if(find_chat_box(receiver).classList.contains('m_chat_box_selected')) handle_my_msg(message);
            }
        });
        create_chat_message.value = '';
        create_chat_username.value = '';
    }
})

const read_file = (src, name, username) => {
    const req = new XMLHttpRequest();
    req.open("GET", src, true);
    req.responseType = "arraybuffer";

    req.onload = (event) => {
    const arrayBuffer = req.response; // Note: not req.responseText
    if (arrayBuffer) {
        const byteArray = new Uint8Array(arrayBuffer);
        socket.emit('msg', text_inp.value, username, (byteArray), name);
        text_inp.value = '';
        // byteArray.forEach((element, index) => {
        // // do something with each byte in the array
        // });
    }
    };

    req.send(null);
}

const handle_send = (e = undefined) => {
    e && e.preventDefault();
    let type = document.getElementsByName('header_name')[0].dataset.type;
    let username = document.getElementsByName('header_name')[0].innerHTML;
    let close_btn = document.querySelector('.m_close');
    let img = document.querySelector('.m_upload_viewer_img');
    if(img.dataset.active === 'true') {
        read_file(img.src, img.dataset.img_name, username);
        close_btn.click();
    }
    else if(text_inp.value && type === 'gp') {
        socket.emit('gp_msg', text_inp.value, username);
        text_inp.value = '';
    }
    else if(text_inp.value) {
        socket.emit('msg', text_inp.value, username);
        if(username === 'exobox') {
            text_inp.disabled = true;
            exo_input = true;
            socket.emit('ai_q', exo_q);
            socket.emit('ai_a', text_inp.value);
            exo_q++;
        }
        text_inp.value = '';
    }
}

window.addEventListener('keydown', e => {
    if(e.key === 'Enter' && document.activeElement === text_inp) {
        handle_send_btn(e);
    }
})

const handle_msg = ({text, _id}, user, avatar) => {
    const type = document.getElementsByName('header_name')[0].dataset.type;
    const hname = document.getElementsByName('header_name')[0].innerHTML;
    chats.innerHTML += `<div data-id=${_id} id=${_id} class="m_flex_row_start m_align_end m_chat_con">
        <div class="m_flex_col_cen" style="align-items: flex-start">
            <p class="m_from">${user}</p>
            <img alt="user" onclick=${`show_info("${user}")`} src="http://5.75.196.210:8888/files/get-user-avatar/${avatar}" class="profile_pic" />
        </div>
        <div class="m_flex_col_cen m_chat_text m_align_end">
        <p>${text}</p>
        <p class="m_text_muted" style="color: #4f4a79!important;">10:28 AM</p>
        </div>
    </div>`;
    chats.lastChild.scrollIntoView();
    socket.emit('seen_messages', hname, type === 'gp');
    handle_chat_delete();
    handle_chat_edit();
}

const handle_my_msg = ({text, _id}) => {
    let my_avatar = document.getElementsByName('my_profile')[0].src;
    chats.innerHTML += `<div data-id=${_id} id=${_id} class="m_flex_row_start m_align_end m_chat_con m_row_rev">
        <div class='m_chat_info_con'>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash-fill m_chat_del" viewBox="0 0 16 16">
                <path d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"/>
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-fill m_chat_edit" viewBox="0 0 16 16">
                <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
            </svg>
        </div>
        <img alt="user" src="${my_avatar}" class="profile_pic" />
        <div class="m_flex_col_cen m_chat_text m_align_end m_my_bg">
        <p>${text}</p>
        <p class="m_text_muted" style="color: white!important;">10:28 AM</p>
        </div>
    </div>`;
    chats.lastChild.scrollIntoView();
    setTimeout(() => {
        let uname = document.getElementsByName('header_name')[0];
        update_last_msg(uname.innerHTML, text);
    }, 550);
    handle_chat_delete();
    handle_chat_edit();
}

socket.on('log', data => {
    console.log(data);
})

const update_last_msg = (username, msg) => {
    if(is_chat_box_there(username)) {
        let cb_names = document.querySelectorAll('.m_chat_name');
        let last_msgs = document.querySelectorAll('.m_chat_last_msg');
        for(let i = 0; i < cb_names.length-1; i++) {
            if(cb_names[i].innerHTML === username) {
                last_msgs[i].innerHTML = msg;
            }
        }
    }
}

socket.on('msg', data => {
    let username = document.getElementsByName('header_name')[0].innerHTML;
    let my_name = document.querySelector('.my_name').innerHTML;
    const {message, sender, avatar, gp_info} = data;
    const {gp_name, is_gp} = gp_info;
    update_last_msg(is_gp ? gp_name : sender, message.text);
    if(sender === 'exobox') {
        text_inp.disabled = false;
        exo_input = false;
        text_inp.focus();
    }
    if(sender === my_name) handle_my_msg(message);
    else if(username === sender || gp_name === username) handle_msg(message, sender, avatar);
    else {
        let t_sender = is_gp ? gp_name : sender;
        create_chat_box(avatar, t_sender, message.text);
        let notif = get_notif(find_chat_box(t_sender));
        notif.innerHTML = Number(notif.innerHTML)+1;
        update_unread_msgs();
        notif.style.display = 'flex';
        // handle notifs
        let t = document.createElement('div');
        t.classList.add('toast');
        t.classList.add('m_alert_info');
        t.role = 'alert';
        t.ariaLive = 'assertive';
        t.ariaAtomic = 'true';
        t.style.display = 'block';
        t.innerHTML = `
            <div class="toast-header m_alert_info">
                <img style='width: 50px; height: 50px;' src="http://5.75.196.210:8888/files/get-user-avatar/${avatar}" class="rounded me-2" alt="...">
                <strong class="me-auto">${sender}${is_gp ? ` (${gp_name})` : ""}</strong>
                <small>11 mins ago</small>
                <!-- <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button> -->
                <svg class="btn-close text-info m_pointer m_notif_btn_close" style="--bs-btn-close-bg: none!important;" xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" data-bs-dismiss="toast" aria-label="Close" viewBox="0 0 16 16">
                    <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
                </svg>
            </div>
            <div class="toast-body">
                ${message.text}
            </div>
        `;
        toasts.push(t);
        document.querySelector('.m_toast_con').appendChild(t);
    }
})

socket.on('delete_msg', ({message_id, delete_all, username}) => {
    let a = document.getElementsByName('header_name')[0];
    let el = document.getElementById(message_id);
    if(el) el.remove();
    if(delete_all) {
        let c = find_chat_box(username);
        if(c) c.remove();
        if(a.innerHTML === username) a.innerHTML = "Dariene Robertson";
    }
    socket.emit('last_msg', username, res => update_last_msg(username, res.message));
})

socket.on('edit_msg', data => {
    let a = document.getElementsByName('header_name')[0].innerHTML;
    const {_id, text, username} = data;
    if(a === username) document.getElementById(_id).children[2] ? document.getElementById(_id).children[2].children[0].innerHTML = text : document.getElementById(_id).children[1].children[0].innerHTML = text;
    socket.emit('last_msg', username, res => update_last_msg(username, res.message));
})

socket.on('add_member', ({avatar, name}) => {
    create_chat_box(avatar, name, 'You have been added to this group!', 'gp');
})

setInterval(() => {
    if(toasts.length) {
        setTimeout(() => {
            if(toasts[0])
            {
                toasts[0].style.display = 'none';
                toasts.shift();
            }
        }, 3000)
    }
}, 500);

const handle_send_btn = (e) => {
    if(!is_edit) {
        handle_send(e);
    } else {
        if(text_inp.value) {
            let a = document.getElementsByName('header_name')[0].innerHTML;
            socket.emit('edit_msg', m_id, text_inp.value, a)
        }
        is_edit = false;
        text_inp.value = '';
    }
}

create_group_btn.addEventListener('click', () => {
    let group_name = document.getElementsByName('create_group_name')[0];
    let group_desc = document.getElementsByName('create_group_description')[0];
    document.getElementsByName('new_chat_popup')[0].classList.add('visually-hidden');
    socket.emit('create_group_channel', group_name.value, group_desc.value, false, res => {
        if(res.success) {
            const {avatar, name} = res;
            create_chat_box(avatar, name, "Welcome to your own group!", 'gp');
            setTimeout(() => find_chat_box(name).click(), 500);
        }
    });
    group_name.value = '';
    group_desc.value = '';
})

send_btn.addEventListener('click', e => {
    handle_send_btn(e);
})

socket.on('connect', () => {
    document.querySelector('.m_socket_loading').classList.add('visually-hidden');
})

socket.on('disconnect', () => {
    document.querySelector('.m_socket_loading').classList.remove('visually-hidden');
})