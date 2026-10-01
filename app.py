const http = require("http");

const PORT = 18231;
const HOST = "0.0.0.0";

const server = http.createServer((req, res) => {
    res.writeHead(200, {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-cache"
    });

    res.end(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SUPER VPN</title>

<style>
*{
    box-sizing:border-box;
    margin:0;
    padding:0;
}

body{
    font-family:Arial,sans-serif;
    color:#fff;
    min-height:100vh;
    background:
        radial-gradient(circle at 20% 10%,#123d72 0,transparent 35%),
        radial-gradient(circle at 80% 30%,#064e63 0,transparent 35%),
        linear-gradient(135deg,#020611,#071526 55%,#02050a);
}

header{
    height:72px;
    padding:0 6%;
    display:flex;
    align-items:center;
    justify-content:space-between;
    border-bottom:1px solid #ffffff14;
    background:#020812aa;
    backdrop-filter:blur(15px);
    position:sticky;
    top:0;
    z-index:100;
}

.logo{
    font-size:23px;
    font-weight:bold;
    letter-spacing:1px;
}

.header-right{
    display:flex;
    align-items:center;
    gap:12px;
}

.profile{
    display:none;
    align-items:center;
    gap:9px;
}

.profile img{
    width:38px;
    height:38px;
    border-radius:50%;
    border:2px solid #2196f3;
}

.email{
    font-size:14px;
    color:#d7e7f8;
}

.menu-button{
    width:44px;
    height:44px;
    border:1px solid #29415e;
    background:#0b1727;
    color:white;
    border-radius:10px;
    font-size:24px;
    cursor:pointer;
}

.menu{
    position:fixed;
    top:72px;
    right:-310px;
    width:290px;
    height:calc(100vh - 72px);
    background:#071321;
    border-left:1px solid #20344c;
    padding:25px;
    transition:.3s;
    z-index:200;
}

.menu.open{
    right:0;
}

.menu h3{
    margin-bottom:20px;
}

.menu-item{
    padding:14px;
    margin-bottom:8px;
    border-radius:10px;
    cursor:pointer;
    color:#d8e5f3;
}

.menu-item:hover{
    background:#10253d;
}

.hero{
    min-height:610px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    padding:50px 20px;
    background-image:
        linear-gradient(#02070f99,#02070fcc),
        radial-gradient(circle at center,#1976d233,transparent 55%);
}

.globe{
    width:125px;
    height:125px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:62px;
    background:
        radial-gradient(circle at 35% 30%,#38bdf8,#075985 55%,#03111f);
    box-shadow:
        0 0 30px #0ea5e959,
        0 0 100px #0ea5e51f;
    margin:0 auto 30px;
}

.hero h1{
    font-size:clamp(40px,9vw,70px);
    margin-bottom:15px;
}

.hero p{
    max-width:650px;
    margin:auto;
    color:#9eb1c7;
    line-height:1.7;
    font-size:17px;
}

.buttons{
    margin-top:35px;
    display:flex;
    justify-content:center;
    gap:14px;
    flex-wrap:wrap;
}

.primary,
.secondary{
    padding:14px 25px;
    border-radius:12px;
    font-size:15px;
    cursor:pointer;
}

.primary{
    color:white;
    border:none;
    background:linear-gradient(135deg,#2563eb,#06b6d4);
}

.secondary{
    color:white;
    background:#0d1b2d;
    border:1px solid #29415e;
}

.section{
    display:none;
    min-height:600px;
    padding:50px 7%;
}

.panel{
    max-width:800px;
    margin:auto;
    background:#0b1727;
    border:1px solid #20344c;
    border-radius:18px;
    padding:28px;
}

.panel h2{
    margin-bottom:15px;
}

.muted{
    color:#8fa2b8;
    line-height:1.6;
}

.form{
    max-width:460px;
    margin:auto;
}

.input{
    width:100%;
    padding:14px;
    margin:8px 0;
    background:#081321;
    border:1px solid #29415e;
    border-radius:10px;
    color:#fff;
}

.select{
    width:100%;
    padding:14px;
    margin:8px 0;
    background:#081321;
    border:1px solid #29415e;
    border-radius:10px;
    color:#fff;
}

.row{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:12px;
}

.api-box,
.server-box{
    padding:17px;
    margin-top:12px;
    background:#081321;
    border:1px solid #20344c;
    border-radius:12px;
}

.badge{
    display:inline-block;
    padding:5px 9px;
    border-radius:8px;
    background:#123a60;
    color:#8bd7ff;
    font-size:12px;
}

.back{
    margin-bottom:20px;
}

textarea{
    resize:vertical;
}

footer{
    text-align:center;
    padding:25px;
    color:#718399;
    border-top:1px solid #17283d;
}

.freedom-bg{
    position:relative;
    overflow:hidden;
}

.freedom-bg:before{
    content:"";
    position:absolute;
    inset:0;
    opacity:.22;
    background:
        radial-gradient(circle,#38bdf8 1px,transparent 2px);
    background-size:45px 45px;
    pointer-events:none;
}

.freedom-content{
    position:relative;
    z-index:2;
}

@media(max-width:600px){
    .email{
        display:none;
    }

    .row{
        grid-template-columns:1fr;
    }
}
</style>
</head>
<body>
<header>
    <div class="logo">⚡ SUPER VPN</div>

    <div class="header-right">

        <div class="profile" id="profile">
            <img id="avatar" src="" alt="profile">
            <span class="email" id="emailText"></span>
        </div>

        <button class="menu-button" onclick="toggleMenu()">☰</button>
    </div>
</header>

<nav class="menu" id="menu">

    <h3>SUPER VPN</h3>

    <div class="menu-item" onclick="showPage('home')">
        🏠 Home
    </div>

    <div class="menu-item" onclick="showPage('account')">
        👤 Account
    </div>

    <div class="menu-item" onclick="showPage('servers')">
        🌍 Servers
    </div>

    <div class="menu-item" onclick="showPage('api')">
        🔑 API
    </div>

    <div class="menu-item" onclick="showPage('telegram')">
        🤖 Telegram Bot
    </div>

    <div class="menu-item" onclick="showPage('support')">
        🎫 Support / Ticket
    </div>

    <div class="menu-item" onclick="showPage('settings')">
        ⚙️ Settings
    </div>

    <div class="menu-item" onclick="logout()">
        🚪 Logout
    </div>

</nav>

<section class="hero page freedom-bg" id="home">

    <div class="freedom-content">

        <div class="globe">
            🌐
        </div>

        <h1>SUPER VPN</h1>

        <p>
            Fast, secure and simple access to your VPN service.
            Manage your account, services and supported configurations
            from one place.
        </p>

        <div class="buttons">

            <button class="primary" onclick="guest()">
                👤 Continue as Guest
            </button>

            <button class="secondary" onclick="showPage('register')">
                🔐 Login / Register
            </button>

        </div>

    </div>

</section>

<section class="section freedom-bg" id="register">

    <div class="panel freedom-content form">

        <div class="back">
            <button class="secondary" onclick="showPage('home')">
                ← Back
            </button>
        </div>

        <h2>🌐 Create your SUPER VPN account</h2>

        <p class="muted">
            Register to access registered-user features.
        </p>

        <input
            class="input"
            id="regEmail"
            type="email"
            placeholder="Email"
        >

        <input
            class="input"
            id="regName"
            type="text"
            placeholder="Name"
        >

        <input
            class="input"
            id="regPassword"
            type="password"
            placeholder="Password"
        >

        <button
            class="primary"
            style="width:100%;margin-top:10px"
            onclick="registerUser()"
        >
            Create Account
        </button>

    </div>

</section>

<section class="section" id="service">

    <div class="panel">

        <h2>Choose your service</h2>

        <p class="muted">
            Choose the supported service/configuration type
            you want to manage.
        </p>

        <select class="select" id="serviceType">

            <option value="V2Ray">
                V2Ray
            </option>

            <option value="Standard VPN">
                Standard VPN
            </option>

            <option value="Other supported configuration">
                Other supported configuration
            </option>

        </select>

        <button
            class="primary"
            onclick="saveService()"
        >
            Continue
        </button>

    </div>

</section>

<section class="section" id="account">

    <div class="panel">

        <h2>👤 Account</h2>

        <p
            class="muted"
            id="accountInfo"
        >
            Not logged in.
        </p>

        <div id="accountDetails"></div>

    </div>

</section>

<section class="section" id="servers">

    <div class="panel">

        <h2>🌍 Servers</h2>

        <p class="muted">
            Server values below are demo values until
            authorized real server infrastructure is connected.
        </p>

        <div class="server-box">
            🇨🇦 Canada — Toronto
            <span class="badge">42 ms demo</span>
        </div>

        <div class="server-box">
            🇨🇦 Canada — Montreal
            <span class="badge">61 ms demo</span>
        </div>

        <div class="server-box">
            🇺🇸 USA — New York
            <span class="badge">78 ms demo</span>
        </div>

        <div class="server-box">
            🇺🇸 USA — Los Angeles
            <span class="badge">166 ms demo</span>
        </div>

        <div class="server-box">
            🇩🇪 Germany — Frankfurt
            <span class="badge">180 ms demo</span>
        </div>

        <div class="server-box">
            🇩🇪 Germany — Berlin
            <span class="badge">181 ms demo</span>
        </div>

        <div class="server-box">
            🇦🇺 Australia — Sydney
            <span class="badge">156 ms demo</span>
        </div>

        <div class="server-box">
            🇦🇺 Australia — Perth
            <span class="badge">224 ms demo</span>
        </div>

        <div class="server-box">
            🇯🇵 Japan — Tokyo
            <span class="badge">198 ms demo</span>
        </div>

    </div>

</section>
<section class="section" id="api">

    <div class="panel">

        <h2>🔑 API Management</h2>

        <p class="muted">
            Only registered users can use API management.
            Each account can have a maximum of 2 API records.
        </p>

        <div id="apiList"></div>

        <button
            class="primary"
            style="margin-top:15px"
            onclick="createApi()"
        >
            ＋ Create API
        </button>

    </div>

</section>

<section class="section" id="telegram">

    <div class="panel">

        <h2>🤖 Telegram Bot</h2>

        <p class="muted">
            SUPER VPN can later connect supported account
            and API management features to the Telegram bot.
        </p>

        <div class="api-box">

            <b>Telegram integration</b>

            <p class="muted">
                Bot connection and server-side authorization
                will be connected through the backend.
            </p>

            <button
                class="secondary"
                style="margin-top:10px"
                onclick="telegramInfo()"
            >
                Open Telegram section
            </button>

        </div>

    </div>

</section>

<section class="section" id="support">

    <div class="panel">

        <h2>🎫 Support / Ticket</h2>

        <p class="muted">
            Send a support request from your SUPER VPN account.
        </p>

        <input
            class="input"
            id="ticketTitle"
            placeholder="Ticket title"
        >

        <textarea
            class="input"
            id="ticketText"
            rows="5"
            placeholder="Describe your issue"
        ></textarea>

        <button
            class="primary"
            onclick="createTicket()"
        >
            Send Ticket
        </button>

        <p
            class="muted"
            style="margin-top:15px"
        >
            Real server-side ticket delivery will be connected
            when the backend/database is added.
        </p>

    </div>

</section>

<section class="section" id="settings">

    <div class="panel">

        <h2>⚙️ Settings</h2>

        <p class="muted">
            SUPER VPN settings.
        </p>

        <div class="api-box">

            <b>Website</b>

            <p class="muted">
                super_vpn.com
            </p>

        </div>

        <div class="api-box">

            <b>Account status</b>

            <p
                class="muted"
                id="settingsStatus"
            >
                Guest
            </p>

        </div>

    </div>

</section>

<section class="features page" id="features">

    <div class="card">

        <div class="card-icon">
            🌍
        </div>

        <h3>
            Global Servers
        </h3>

        <p>
            Choose from available server locations.
        </p>

    </div>

    <div class="card">

        <div class="card-icon">
            ⚡
        </div>

        <h3>
            Fast Connection
        </h3>

        <p>
            View server information and connection status.
        </p>

    </div>

    <div class="card">

        <div class="card-icon">
            🔑
        </div>

        <h3>
            API Management
        </h3>

        <p>
            Registered users can manage up to two API records.
        </p>

    </div>

    <div class="card">

        <div class="card-icon">
            🤖
        </div>

        <h3>
            Telegram Bot
        </h3>

        <p>
            Telegram integration is planned for the backend.
        </p>

    </div>

</section>

<footer>
    © 2026 SUPER VPN • super_vpn.com
</footer>
<script>

let user =
    JSON.parse(
        localStorage.getItem("supervpn_user") || "null"
    );

let apis =
    JSON.parse(
        localStorage.getItem("supervpn_apis") || "[]"
    );

let tickets =
    JSON.parse(
        localStorage.getItem("supervpn_tickets") || "[]"
    );

function toggleMenu(){

    document
        .getElementById("menu")
        .classList
        .toggle("open");

}

function hideAll(){

    document
        .querySelectorAll(".page,.section")
        .forEach(
            element => element.style.display = "none"
        );

}

function showPage(id){

    hideAll();

    const element =
        document.getElementById(id);

    if(!element){
        return;
    }

    if(
        id === "home" ||
        id === "features"
    ){

        element.style.display = "flex";

    }else{

        element.style.display = "block";

    }

    document
        .getElementById("menu")
        .classList
        .remove("open");

    if(id === "api"){
        renderApis();
    }

    if(id === "account"){
        renderAccount();
    }

    updateProfile();

}

function guest(){

    alert(
        "Guest mode is available. Registered-only features require an account."
    );

}

function registerUser(){

    const email =
        document
        .getElementById("regEmail")
        .value
        .trim();

    const name =
        document
        .getElementById("regName")
        .value
        .trim();

    const password =
        document
        .getElementById("regPassword")
        .value;

    if(!email || !name || !password){

        alert(
            "Please fill all fields."
        );

        return;
    }

    if(!email.includes("@")){

        alert(
            "Please enter a valid email."
        );

        return;
    }

    user = {

        email: email,

        name: name,

        service: null,

        avatar:
            "https://ui-avatars.com/api/?name=" +
            encodeURIComponent(name) +
            "&background=1677ff&color=fff"

    };

    localStorage.setItem(
        "supervpn_user",
        JSON.stringify(user)
    );

    updateProfile();

    alert(
        "Registration completed. Now choose your service."
    );

    showPage("service");

}

function saveService(){

    if(!user){

        showPage("register");

        return;
    }

    user.service =
        document
        .getElementById("serviceType")
        .value;

    localStorage.setItem(
        "supervpn_user",
        JSON.stringify(user)
    );

    alert(
        "Service selected: " +
        user.service
    );

    showPage("account");

}

function updateProfile(){

    const profile =
        document.getElementById("profile");

    if(user){

        profile.style.display = "flex";

        document
            .getElementById("emailText")
            .textContent = user.email;

        document
            .getElementById("avatar")
            .src = user.avatar;

        const status =
            document.getElementById(
                "settingsStatus"
            );

        if(status){

            status.textContent =
                "Registered";

        }

    }else{

        profile.style.display = "none";

        const status =
            document.getElementById(
                "settingsStatus"
            );

        if(status){

            status.textContent =
                "Guest";

        }

    }

}
function renderAccount(){

    const info =
        document.getElementById(
            "accountInfo"
        );

    const details =
        document.getElementById(
            "accountDetails"
        );

    if(!user){

        info.textContent =
            "Not logged in.";

        details.innerHTML = "";

        return;
    }

    info.textContent =
        "Your SUPER VPN account";

    details.innerHTML = `

        <div class="api-box">

            <b>Email</b>

            <p class="muted">
                ${escapeHtml(user.email)}
            </p>

        </div>

        <div class="api-box">

            <b>Name</b>

            <p class="muted">
                ${escapeHtml(user.name)}
            </p>

        </div>

        <div class="api-box">

            <b>Selected service</b>

            <p class="muted">
                ${escapeHtml(
                    user.service || "Not selected"
                )}
            </p>

        </div>

    `;

}

function createApi(){

    if(!user){

        alert(
            "You must register first to use API management."
        );

        showPage("register");

        return;
    }

    if(apis.length >= 2){

        alert(
            "Maximum 2 API records are allowed."
        );

        return;
    }

    const api = {

        id: Date.now(),

        name:
            "API " +
            (apis.length + 1),

        created:
            new Date().toISOString()

    };

    apis.push(api);

    localStorage.setItem(
        "supervpn_apis",
        JSON.stringify(apis)
    );

    renderApis();

}

function deleteApi(id){

    if(!user){

        return;
    }

    apis =
        apis.filter(
            api => api.id !== id
        );

    localStorage.setItem(
        "supervpn_apis",
        JSON.stringify(apis)
    );

    renderApis();

}

function renderApis(){

    const box =
        document.getElementById(
            "apiList"
        );

    if(!box){
        return;
    }

    box.innerHTML = "";

    if(!user){

        box.innerHTML =
            '<p class="muted">Register first to use API management.</p>';

        return;
    }

    if(apis.length === 0){

        box.innerHTML =
            '<p class="muted">No API created yet.</p>';

        return;
    }

    apis.forEach(api => {

        box.innerHTML += `

            <div class="api-box">

                <b>
                    ${escapeHtml(api.name)}
                </b>

                <br>

                <span class="muted">
                    Created:
                    ${new Date(
                        api.created
                    ).toLocaleString()}
                </span>

                <br>

                <button
                    class="secondary"
                    style="margin-top:10px"
                    onclick="deleteApi(${api.id})"
                >
                    Delete API
                </button>

            </div>

        `;

    });

}

function createTicket(){

    if(!user){

        alert(
            "Register first to create a ticket."
        );

        showPage("register");

        return;
    }

    const title =
        document
        .getElementById("ticketTitle")
        .value
        .trim();

    const text =
        document
        .getElementById("ticketText")
        .value
        .trim();

    if(!title || !text){

        alert(
            "Please fill the ticket title and message."
        );

        return;
    }

    const ticket = {

        id: Date.now(),

        email: user.email,

        title: title,

        text: text,

        created:
            new Date().toISOString(),

        status: "pending"

    };

    tickets.push(ticket);

    localStorage.setItem(
        "supervpn_tickets",
        JSON.stringify(tickets)
    );

    document
        .getElementById("ticketTitle")
        .value = "";

    document
        .getElementById("ticketText")
        .value = "";

    alert(
        "Ticket created successfully."
    );

}

function telegramInfo(){

    alert(
        "Telegram integration will use the SUPER VPN backend and account authorization."
    );

}

function logout(){

    user = null;

    apis = [];

    tickets = [];

    localStorage.removeItem(
        "supervpn_user"
    );

    localStorage.removeItem(
        "supervpn_apis"
    );

    localStorage.removeItem(
        "supervpn_tickets"
    );

    updateProfile();

    showPage("home");

}

function escapeHtml(value){

    return String(value)
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");

}
updateProfile();

showPage("home");

</script>

</body>
</html>
`);

});

server.listen(PORT, HOST, () => {

    console.log(
        "SUPER VPN is running on port " +
        PORT
    );

});