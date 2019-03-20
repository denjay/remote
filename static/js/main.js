// 缓存当前ip
var ip = window.location.host.split(":")[0]
if (ip) {
    window.localStorage.setItem("ip", ip)
}

// 给按钮绑定事件
document.getElementById('play-or-pause').addEventListener('click', () => (send_code('hot_key', {
    description: '播放/暂停'
})))
document.getElementById('volume-plus').addEventListener('click', () => (send_code('hot_key', {
    description: '音量加'
})))
document.getElementById('next').addEventListener('click', () => (send_code('hot_key', {
    description: '下一曲'
})))
document.getElementById('volume-reduction').addEventListener('click', () => (send_code('hot_key', {
    description: '音量减'
})))
document.getElementById('previous').addEventListener('click', () => (send_code('hot_key', {
    description: '上一曲'
})))

// 给底部导航栏绑定事件
document.querySelectorAll("ul li").forEach((item, index) => {
    item.addEventListener("click", () => {
        toggle(index)
    })
});

function toggle(index_outer) {
    document.querySelectorAll("#container > div").forEach((item, index_inner) => {
        if (index_inner === index_outer) {
            item.style.display = "inline";
        } else {
            item.style.display = "none";
        }
    });
    document.querySelectorAll("ul li").forEach((item, index_inner) => {
        if (index_inner === index_outer) {
            item.style.borderTop = "2px yellow solid"
        } else {
            item.style.borderTop = "2px #00D1B2 solid"
        }
    });
}

// 获取匹配码
var match_code
window.location.search.substr(1).split("&").forEach((item, index, arr) => {
    if (item.split("=")[0] == "match") {
        match_code = item.split("=")[1]
        document.getElementsByTagName("input")[0].value = match_code
    }
})

var front_end_config
send_code("configuration") // 获取前端配置

// 应用配置到switch
function refresh_switch() {
    document.querySelectorAll(".switch").forEach((item, index) => {
        if ((Math.pow(2, index) & front_end_config) === Math.pow(2, index)) {
            item.style.backgroundColor = "rgb(19, 206, 102)";
            document.querySelectorAll("#set div")[index].classList.add("is-chicked")
        } else {
            item.style.backgroundColor = "gray";
            document.querySelectorAll("#set div")[index].classList.remove("is-chicked")
        }
    })
}

// 给switch绑定事件,修改配置
document.querySelectorAll(".switch").forEach((item, index_outer) => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".switch").forEach((_, index_inner) => {
            if (index_outer === index_inner) {
                if ((Math.pow(2, index_inner) & front_end_config) === Math.pow(2, index_inner)) {
                    var new_front_end_config = front_end_config - Math.pow(2, index_inner)
                } else {
                    var new_front_end_config = front_end_config + Math.pow(2, index_inner)
                }
                if (! new_front_end_config) {
                    console.log(new_front_end_config)
                    new_front_end_config = 0
                }
                send_code("configuration", {
                    "front_end_config": new_front_end_config
                })
            }
        })
    })
})

// 旋转效果
function rotate() {
    if ((0b0001 & front_end_config) !== 0b0001) {
        document.getElementById('buttons-wrapper').classList.add("rotate-wrapper")
        document.querySelectorAll("#buttons-wrapper i").forEach((item, index, arr) => {
            item.classList.add("rotate-icon")
        })
    } else {
        document.getElementById('buttons-wrapper').classList.remove("rotate-wrapper")
        document.querySelectorAll("#buttons-wrapper i").forEach((item, index, arr) => {
            item.classList.remove("rotate-icon")
        })
    }
}

// 获取本机ip地址
var local_ip = null

function getIP(onNewIP) { //  onNewIp - your listener function for new IPs
    var myPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection; //compatibility for firefox and chrome
    var pc = new myPeerConnection({
            iceServers: []
        }), // 空的ICE服务器（STUN或者TURN）
        noop = function () {},
        localIPs = {}, //记录有没有被调用到onNewIP这个listener上
        ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g,
        key;

    function ipIterate(ip) {
        if (!localIPs[ip]) onNewIP(ip);
        localIPs[ip] = true;
    }
    pc.createDataChannel(""); //create a bogus data channel
    pc.createOffer().then(function (sdp) {
        sdp.sdp.split('\n').forEach(function (line) {
            if (line.indexOf('candidate') < 0) return;
            line.match(ipRegex).forEach(ipIterate);
        });
        pc.setLocalDescription(sdp, noop, noop);
    }); // create offer and set local description
    pc.onicecandidate = function (ice) { //listen for candidate events
        if (!ice || !ice.candidate || !ice.candidate.candidate || !ice.candidate.candidate.match(ipRegex))
            return;
        ice.candidate.candidate.match(ipRegex).forEach(ipIterate);
    };
}

function set_clipboard_content() {
    let content = document.getElementsByTagName("textarea")[0].value
    send_code('set_clipboard_content', {
        content: content
    })
}

var ul_el = document.getElementsByTagName("ul")[0]
// 群发请求,nsid是网络号
function mass(path, nsid_or_ip, params) {
    if ("ip" in nsid_or_ip) {
        var time = 3000;
        var nsid = nsid_or_ip.ip.split(".").slice(0, 3).join(".") + ".";
        var start = Number(nsid_or_ip.ip.split(".")[3]);
        var end = start + 1;
    } else {
        var time = 10000;
        var nsid = nsid_or_ip.nsid;
        var start = 0;
        var end = 255;
    }
    var pormises = [];
    for (var i = start; i < end; i++) {
        let p = new Promise((resolve, reject) => {
            let ip = nsid + i;
            let ajax = new XMLHttpRequest();
            ajax.open('post', `http://${ip}:8765/${path}`);
            ajax.setRequestHeader('content-type', 'application/json');
            ajax.send(params);
            ajax.onreadystatechange = function () {
                if (ajax.readyState == 4 && ajax.status == 200) {
                    window.localStorage.setItem("ip", ajax.responseURL.match(/\/\/(.*?):/)[1]); // 更新缓存的ip
                    resolve(JSON.parse(ajax.responseText));
                } else if ("ip" in nsid_or_ip && ajax.readyState == 4 && ajax.status != 200) { // nsid_or_ip为ip时可跳过超时
                    reject("请求失败")
                }
            }
        });
        pormises.push(p)
    };
    let p = new Promise((resolve, reject) => {
        setTimeout(() => {
            reject("超时，请重试！")
        }, time)
    });
    pormises.push(p);
    return pormises
}
// 弹出消息框
function show_message(message) {
    if (!((0b0010 & front_end_config) === 0b0010 && (message === 0))) {
        message = (message === 0) ? "命令执行成功" : message;
        document.getElementById("message").innerHTML = message;
        document.getElementById("message").style.visibility = 'visible';
        setTimeout(() => {
            document.getElementById("message").style.visibility = 'hidden';
        }, 2000)
    }
}
// 处理从服务器收到的json消息
function handle_response(result) {
    if (result.file_url) {
        window.location.href = result.file_url;
    } else if (result.text) {
        var textarea_el = document.getElementsByTagName("textarea")[0]
        textarea_el.value = result.text
    } else if (result.message != undefined) {
        show_message(result.message)
    } else if (result.front_end_config != undefined) {
        front_end_config = result.front_end_config
        refresh_switch()
        rotate()
    }
}

// 发送请求
function send_code(path, params) {
    var match_code = document.getElementsByTagName("input")[0].value
    if (params) {
        params["match_code"] = match_code
    } else {
        params = {
            "match_code": match_code
        }
    }
    params = JSON.stringify(params)
    let ip = window.localStorage.getItem("ip")
    ip = ip ? ip : "0.0.0.0";
    let pormises = mass(path, {
        ip: ip
    }, params)
    Promise.race(pormises).then((result) => {
        handle_response(result)
    }).catch((error) => {
        // 如果知道本机IP，就向所在局域网发送请求
        getIP(function (ip) {
            local_ip = ip
            var nsid = ip.split(".").slice(0, 3).join(".") + "."; // 网络号
            let pormises = mass(path, {
                nsid: nsid
            }, params);
            Promise.race(pormises).then((result) => {
                handle_response(result)
            }).catch((error) => {
                show_message(error);
            })
        });
        // 向localstorage中的网络号发送请求
        setTimeout(() => {
            if (!local_ip) {
                if (window.localStorage.getItem("ip")) {
                    var nsid = window.localStorage.getItem("ip").split(".").slice(0, 3).join(".") + ".";
                    let pormises = mass(path, {
                        nsid: nsid
                    }, params);
                    Promise.race(pormises).then((result) => {
                        handle_response(result)
                    }).catch((error) => {
                        show_message(error);
                    })
                }
            }
        }, 3000)
    })
}