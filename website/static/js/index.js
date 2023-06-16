let alerts = document.querySelectorAll('.alert');

function get_cookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
}

if(alerts) {
    alerts.forEach((a, i) => {
        setTimeout(() => {
            a.style.display = 'none';
        }, 5000)
    })
}

const handle_select = (container_class, selected_class, selected) => {
    let svg_cons = document.querySelectorAll(container_class);
    let selected_items = document.querySelectorAll(`.${selected_class}`);
    selected === -99 && selected_items.forEach(item => {
        item.classList.remove(selected_class);
    })
    svg_cons.forEach((c, i) => {
        c.addEventListener('click', () => {
            if(selected === i) return;
            if(svg_cons[selected]) svg_cons[selected].classList.remove(selected_class);
            c.classList.add(selected_class);
            selected = i;
        })
    })
}

const handle_logout = () => {
    let el = document.getElementsByName('logout')[0];
    el.addEventListener('click', () => {
        window.location = '/auth/logout'
    })
}

const handle_logic = () => {
    let nav_icons = document.querySelectorAll('.m_nav_svg_con');
    let messages = document.querySelector('.m_messages');
    nav_icons.forEach((c, i) => {
        c.addEventListener('click', () => {
            setTimeout(() => {
                if(nav_icons[1].classList.contains('m_nav_svg_con_selected')) {
                    messages.style.height = 'calc(100% - 40px)';
                    messages.style.visibility = 'visible';
                } else if(nav_icons[0].classList.contains('m_nav_svg_con_selected')) {
                    messages.style.height = '0';
                    messages.style.visibility = 'hidden';
                } else if(nav_icons[2].classList.contains('m_nav_svg_con_selected')) {
                    messages.style.height = '0';
                    messages.style.visibility = 'hidden';
                }
            }, 100);
        })
    })
}

const get_name = (el) => {
    let name = "";
    let name_start = el.innerHTML.search('m_chat_name')+11+2;
    let arr = el.innerHTML.split("");
    for(let i = name_start; i < el.innerHTML.length; i++) {
        if(arr[i] === '<') break;
        name += arr[i];
    }
    return name;
}

const get_src = (el) => {
    let src = "";
    let src_start = el.innerHTML.search('src')+3+2;
    let arr = el.innerHTML.split("");
    for(let i = src_start; i < el.innerHTML.length; i++) {
        if(arr[i] === '"') break;
        src += arr[i];
    }
    return src;
}

const find_chat_box = username => {
    let cb_names = document.querySelectorAll('.m_chat_name');
    for(let i = 0; i < cb_names.length-1; i++) {
        if(cb_names[i].innerHTML === username) {
            let d = cb_names[i];
            while(!(d.classList.contains('m_chat_box'))) {
                d = d.parentElement;
            }
            return d;
        }
    }
}

const get_notif = chat_box => {
    return chat_box.children[1].children[1];
}

const update_unread_msgs = () => {
    let unread_msgs = document.querySelector('.m_notif_number');
    let els = document.querySelectorAll('.m_chat_box_notif');
    let new_msgs = 0;
    els.forEach(el => {
        new_msgs += Number(el.innerHTML);
    })
    unread_msgs.innerHTML = new_msgs;
    if(new_msgs === 0) {
        unread_msgs.classList.add('visually-hidden');
    } else {
        unread_msgs.classList.remove('visually-hidden');
    }
}

const handle_chats = () => {
    let els = document.querySelectorAll('.m_chat_box');
    let inp = document.querySelector('.m_text_inp');
    let header_name = document.getElementsByName('header_name')[0];
    let header_prof = document.getElementsByName('header_prof')[0];
    let chats = document.querySelector('.m_chats');
    let my_profile = document.getElementsByName('my_profile')[0].src;
    let text_inp = document.querySelector('.m_text_inp');
    els.forEach((el, i) => {
        el.addEventListener('click', e => {
            let d = e.target;
            while(!(d.parentElement.classList.contains('m_chat_box_con'))) {
                d = d.parentElement;
            }
            let name = get_name(d);
            let notif = get_notif(find_chat_box(name));
            let type = el.dataset.type;
            if(name === 'exobox')   text_inp.disabled = exo_input;
            else                    text_inp.disabled = false;
            notif.innerHTML = '0';
            notif.style.display = 'none';
            //if(header_name.innerHTML === name) return;
            let me;
            socket.emit('me', res => me = res.name);
            update_unread_msgs();
            is_edit = false;
            document.querySelector('.m_text_inp').value = '';
            socket.emit('seen_messages', name, type === 'gp');
            header_name.innerHTML = name;
            header_name.dataset.type = type;
            let src = get_src(d);
            header_prof.src = src;
            inp.focus();
            // turn on loading
            chats.innerHTML = `
            <?xml version="1.0" encoding="utf-8"?>
            <svg class="m_loading" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto; background: transparent; display: block; shape-rendering: auto;" width="50px" height="50px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
            <path fill="none" stroke="#406ae0" stroke-width="8" stroke-dasharray="42.76482137044271 42.76482137044271" d="M24.3 30C11.4 30 5 43.3 5 50s6.4 20 19.3 20c19.3 0 32.1-40 51.4-40 C88.6 30 95 43.3 95 50s-6.4 20-19.3 20C56.4 70 43.6 30 24.3 30z" stroke-linecap="round" style="transform:scale(0.8);transform-origin:50px 50px">
              <animate attributeName="stroke-dashoffset" repeatCount="indefinite" dur="1s" keyTimes="0;1" values="0;256.58892822265625"></animate>
            </path>
            <!-- [ldio] generated by https://loading.io/ --></svg>
            `
            fetch(`http://5.75.196.210:8888/${type}-chat/${name}?offset=0`).then(res => {
                return res.json()
            }).then(res => {
                chats.innerHTML = ''
                // turn off loading
                res.forEach(msg => {
                    const {_id, date, file, from, text, avatar} = msg;
                    chats.innerHTML += `
                    <div data-id=${_id} id=${_id} class="m_flex_row_start m_align_end m_chat_con ${from === me && 'm_row_rev'}">
                        ${from === me ? `
                            <div class='m_chat_info_con'>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash-fill m_chat_del" viewBox="0 0 16 16">
                                    <path d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"/>
                                </svg>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-fill m_chat_edit" viewBox="0 0 16 16">
                                    <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
                                </svg>
                            </div>
                        ` : ``}
                        <div class="m_flex_col_cen" ${from !== me ? 'style="align-items: flex-start"' : ''}>
                            ${from !== me ? `<p class="m_from">${from}</p>` : ``}
                            <img ${from !== me && `onclick='show_info("${from}")'`} alt="user" src="${from === me ? my_profile : `http://5.75.196.210:8888/files/get-user-avatar/${avatar}`}" class="profile_pic" />
                        </div>
                        <div class="m_flex_col_cen m_chat_text m_align_end ${from === me && 'm_my_bg'}">
                            <p>${text}</p>
                            <p class="m_text_muted" style="color: ${from === me ? 'white' : '#4f4a79'}!important;">10:28 AM</p>
                        </div>
                    </div>
                    `
                })
                handle_chat_delete();
                handle_chat_edit();
                chats.lastElementChild.scrollIntoView();
            }).catch(err => console.log(err));
        })
    })
}

const handle_profile_upload = () => {
    let el = document.querySelector('.m_upload_prof');
    let img = document.getElementsByName('my_own_profile_pic')[0];
    let input = document.querySelector('.hidden_file_inp');
    let update_profile_form = document.getElementsByName('update_profile')[0];

    el.addEventListener('click', () => {
        input.accept = '.png, .jpg, .jpeg';

        input.onchange = e => { 
            var file = e.target.files[0];
            if(file.type === 'image/png' || file.type === 'image/jpg' || file.type === 'image/jpeg') {
                img.src = URL.createObjectURL(file);
            }
        }

        input.click();
    })
}

const handle_file_input = () => {
    let el = document.querySelector('.file_input');
    let img_con = document.querySelector('.m_upload_viewer');
    let img = document.querySelector('.m_upload_viewer_img');
    let close_btn = document.querySelector('.m_close');
    let title = document.querySelector('.m_upload_viewer_title');
    close_btn.addEventListener('click', () => {
        img_con.classList.add('visually-hidden');
        img.dataset.active = false;
    })
    el.addEventListener('click', () => {
        var input = document.createElement('input');
        input.type = 'file';
        input.name = 'file_input'
        // input.accept = '.png, .jpg, .jpeg';

        input.onchange = e => { 
            var file = e.target.files[0];
            // if(file.type === 'image/png' || file.type === 'image/jpg' || file.type === 'image/jpeg') {
            if(true) {
                img.src = URL.createObjectURL(file);
                img.dataset.img_name = file.name;
                img.dataset.active = true;
                title.innerHTML = file.name;
                img_con.classList.remove('visually-hidden');
            } else {
                // later on we should change this and show a little docs icon
                img_con.classList.add('visually-hidden');
            }
        }

        input.click();
    })
}

const handle_profile_popup = () => {
    let my_profile = document.getElementsByName('my_profile')[0];
    let my_profile_popup = document.getElementsByName('my_profile_popup')[0];
    my_profile.addEventListener('click', () => {
        my_profile_popup.classList.remove('visually-hidden');
    })
    my_profile_popup.addEventListener('click', e => {
        if(e.target === my_profile_popup) my_profile_popup.classList.add('visually-hidden');
    })
}

const handle_create_chat_popup = () => {
    let create_new_chat = document.querySelector('.m_create_new_chat');
    let new_chat_popup = document.getElementsByName('new_chat_popup')[0];
    create_new_chat.addEventListener('click', () => {
        new_chat_popup.classList.remove('visually-hidden');
    })
    new_chat_popup.addEventListener('click', e => {
        if(e.target === new_chat_popup) new_chat_popup.classList.add('visually-hidden');
    })
}

const clear_toasts = () => {
    setInterval(() => {
        let toasts = document.querySelectorAll('.toast');
        toasts.forEach(t => {
            t.style.display = 'none';
        })
    }, 6000);
}

const show_info = (username, type = 'user') => {
    type = type === 'pv' ? 'user' : type;
    let ppc = document.createElement('div');
    let pp = document.createElement('div');
    ppc.classList.add('m_profile_popup_con');
    pp.classList.add('m_absolute_center');
    pp.classList.add('m_profile_popup');
    ppc.addEventListener('click', e => {
        if(e.target === ppc) {
            ppc.remove();
        }
    })
    ppc.appendChild(pp);
    pp.innerHTML = `
        <?xml version="1.0" encoding="utf-8"?>
        <svg class="m_loading" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto; background: transparent; display: block; shape-rendering: auto;" width="50px" height="50px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
        <path fill="none" stroke="#406ae0" stroke-width="8" stroke-dasharray="42.76482137044271 42.76482137044271" d="M24.3 30C11.4 30 5 43.3 5 50s6.4 20 19.3 20c19.3 0 32.1-40 51.4-40 C88.6 30 95 43.3 95 50s-6.4 20-19.3 20C56.4 70 43.6 30 24.3 30z" stroke-linecap="round" style="transform:scale(0.8);transform-origin:50px 50px">
        <animate attributeName="stroke-dashoffset" repeatCount="indefinite" dur="1s" keyTimes="0;1" values="0;256.58892822265625"></animate>
        </path>
        <!-- [ldio] generated by https://loading.io/ --></svg>
    `;
    fetch(`http://5.75.196.210:8888/${type}-info/${username}`).then(res => res.json()).then(res => {
        if(type === 'user') {
            let {avatar, bio} = res;
            pp.innerHTML = `
                <h1 style="margin: 1rem; color: white; font-size: 30px; font-weight: bold;">${username}'s Profile</h1>
                <div class="m_image_upload_con">
                    <img alt="${username}'s Profile" src="http://5.75.196.210:8888/files/get-user-avatar/${avatar}" name="my_own_profile_pic" class="profile_pic m_profile_lg mb-3" />
                </div>
                <div class="form-floating m_form_posing mb-3">
                    <input type="text" readonly class="form-control m_inp" id="floatingPlaintextInput" value="${username}">
                    <label for="floatingPlaintextInput">Username</label>
                </div>
                <div class="form-floating m_form_posing mb-3">
                    <textarea readonly name="bio" style="min-height: 100px;" class="form-control m_inp" placeholder="Tell us about yourself..." id="floatingTextarea">${bio}</textarea>
                    <label for="floatingTextarea">Bio</label>
                </div>
            `
        } else {
            const {avatar, description, members, name} = res;
            pp.innerHTML = `
                <h1 style="margin: 1rem; color: white; font-size: 30px; font-weight: bold;">${name}'s Profile</h1>
                <div class="m_image_upload_con">
                    <img alt="${name}'s Profile" src="http://5.75.196.210:8888/files/get-user-avatar/${avatar}" name="my_own_profile_pic" class="profile_pic m_profile_lg mb-3" />
                </div>
                <div class="form-floating m_form_posing mb-3">
                    <input type="text" readonly class="form-control m_inp" id="floatingPlaintextInput" value="${name}">
                    <label for="floatingPlaintextInput">Group name</label>
                </div>
                <div class="form-floating m_form_posing mb-3">
                    <textarea readonly name="bio" style="min-height: 100px;" class="form-control m_inp" placeholder="Tell us about yourself..." id="floatingTextarea">${description}</textarea>
                    <label for="floatingTextarea">Description</label>
                </div>
            `
        }
    }).catch(e => console.log(e));
    document.querySelector('body').appendChild(ppc);
}

const handle_selected_profile_info = () => {
    let header_name = document.getElementsByName('header_name')[0];
    const el = document.getElementsByName('selected_profile_info')[0];
    el.addEventListener('click', () => show_info(header_name.innerHTML, header_name.dataset.type));
}

const handle_chat_delete = () => {
    let header_name = document.getElementsByName('header_name')[0].innerHTML;
    let els = document.querySelectorAll('.m_chat_del');
    let my_chats = document.querySelectorAll('.m_row_rev');
    els.forEach((el, i) => {
        el.addEventListener('click', () => {
            socket.emit('delete_msg', my_chats[i].dataset.id, header_name);
        })
    })
}

const handle_chat_edit = () => {
    let els = document.querySelectorAll('.m_chat_edit');
    let texts = document.querySelectorAll('.m_my_bg p');
    let inp = document.querySelector('.m_text_inp');
    let my_chats = document.querySelectorAll('.m_row_rev');
    els.forEach((el, i) => {
        el.addEventListener('click', () => {
            inp.focus();
            inp.value = texts[i*2].innerHTML;
            is_edit = true;
            m_id = my_chats[i].dataset.id;
        })
    })
}

const handle_context_selector = () => {
    let els = document.querySelectorAll('.m_context_selector p');
    let contexts = document.getElementsByName('context');
    els.forEach((el, i) => {
        el.addEventListener('click', e => {
            let selected = document.querySelector('.m_context_selected');
            if(e.target === selected) return;
            else {
                selected.classList.remove('m_context_selected');
                el.classList.add('m_context_selected');
                contexts.forEach(c => c.classList.add('visually-hidden'));
                contexts[Number(el.dataset.name)].classList.remove('visually-hidden');
            }
        })
    })
}

const handle_options = () => {
    const m_options = document.querySelector('.m_options');
    const m_dd = document.querySelector('.m_dd');
    m_options.addEventListener('click', () => {
        setTimeout(() => {
            m_dd.classList.remove('visually-hidden');
        }, 100)
    })
    document.querySelector('body').addEventListener('click', () => {
        m_dd.classList.add('visually-hidden');
    })
}

document.querySelector('.add_member_btn').addEventListener('click', () => {
    let ppc = document.createElement('div');
    ppc.classList.add('add_member_popup');
    let pp = document.createElement('div');
    ppc.classList.add('m_profile_popup_con');
    pp.classList.add('m_absolute_center');
    pp.classList.add('m_profile_popup');
    pp.style = `display: flex;align-items: center;justify-content: center;flex-direction: column;`
    ppc.addEventListener('click', e => {
        if(e.target === ppc) {
            ppc.remove();
        }
    })
    ppc.appendChild(pp);
    pp.innerHTML = `
        <h1 style="margin: 1rem; color: white; font-size: 30px; font-weight: bold;">Add Member</h1>
        <div class="form-floating m_form_posing mb-3" style="margin: 1rem auto!important;">
            <input name="add_member_name" type="text" class="form-control m_inp" id="floatingInputValue" placeholder="Enter his name here">
            <label for="floatingInputValue">Enter his/her name here</label>
        </div>
        <button onclick="add_member()" type="button" name="add_member" class="btn btn-primary">Add</button>
    `
    document.querySelector('body').appendChild(ppc);
})

const add_member = () => {
    let in_name = document.getElementsByName('add_member_name')[0];
    let header = document.getElementsByName('header_name')[0];
    if(header.dataset.type !== 'gp') return document.querySelector('.add_member_popup').remove();
    socket.emit('add_member', in_name.value, header.innerHTML);
    in_name.value = '';
    document.querySelector('.add_member_popup').remove();
}

const is_exo = () => {
    let loc = window.location.href;
    let flag_pos = loc.indexOf("?");
    if(flag_pos !== -1)
    {
        let flag = loc.substring(flag_pos+1);
        if(flag === "exo")
        {
            socket.emit('ai');
            console.log('ai present');
        }
    }
}

// not decided to put this or not
// clear_toasts();

is_exo();

handle_options();

handle_context_selector();

update_unread_msgs();

handle_selected_profile_info();

handle_profile_popup();
handle_profile_upload();

handle_create_chat_popup();

handle_logic();
handle_chats();

handle_select('.m_nav_svg_con', 'm_nav_svg_con_selected', 1);
handle_select('.m_chat_box', 'm_chat_box_selected', -99);

handle_file_input();
handle_logout();