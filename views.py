import hashlib
import time
import requests
import functools
from flask import session, render_template, redirect, request, abort, jsonify
from app import app, db
from models import DoorLog
from sqlalchemy import Column, func

start_time = int(time.time())
door_map = {}


def make_door_map(doors):
    return {str(door["id"]): door["equipmentCode"] for door in doors}


def login_ok():
    return session.get('username') and session.get('access_token')


def check_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not login_ok():
            return redirect("/login")
        return func(*args, **kwargs)

    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if login_ok():
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template("login.html", error="请输入用户名或密码", start_time=start_time)
        resp = requests.get(
            f"http://www.svpypark.com/clientUser/mobile/login.do?userName={username}&password={password}")
        if resp.status_code != 200:
            return abort(resp.status_code)
        result = resp.json()
        if int(result["app_result_key"]) == 0 and result["access_token"]:
            session['username'] = username
            session['access_token'] = result['access_token']
            session.permanent = True
            return redirect('/')
        else:
            return render_template("login.html", error=result.get("app_result_message_key", "未知错误"),
                                   start_time=start_time)
    else:
        return render_template("login.html", start_time=start_time)


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


def get_auth_parameters(token):
    st = int(time.time() * 1000)
    return {"access_token": token, "st": st,
            "signature": hashlib.md5(("smartiABC" + str(st) + token).encode("utf8")).hexdigest()}


@app.route('/', methods=['GET'])
@check_login
def index():
    resp = requests.post("http://www.svpypark.com/entrance/getRoomList.do",
                         data={"pageNo": 1, "pageSize": 100, **get_auth_parameters(session["access_token"])})
    if resp.status_code != 200:
        return abort(resp.status_code)
    result = resp.json()
    if int(result["app_result_key"]) == 0:
        door_map[session["username"]] = make_door_map(result.get("list", []))
        door_hist = {
            door.door_name: count for door, count in
            db.session.query(DoorLog, func.count(DoorLog.id)).filter_by(username=session["username"], code=0)
            .group_by(DoorLog.door_name)
            .order_by(func.count(DoorLog.id).desc())[-4:]
        }
        freq_list = []
        door_list = []
        for x in result.get('list', []):
            if x["equipmentCode"] in door_hist:
                freq_list.append(x)
            else:
                door_list.append(x)
        freq_list.sort(key=lambda d: door_hist[d["equipmentCode"]], reverse=True)
        return render_template("index.html", freq_doors=freq_list, doors=door_list, username=session["username"])
    return abort(500)


@check_login
@app.route('/open/<door_id>', methods=['GET'])
def open_door(door_id):
    resp = requests.post('http://www.svpypark.com/entrance/openDoor.do',
                         data={"id": door_id, **get_auth_parameters(session["access_token"])})
    if resp.status_code != 200:
        db.session.add(DoorLog(username=session["username"], door_id=door_id,
                               door_name=door_map.get(session["username"], {}).get(door_id), code=resp.status_code,
                               msg="服务器错误"))
        db.session.commit()
        return abort(resp.status_code)
    result = resp.json()
    system_result_key = int(result["system_result_key"])
    app_result_key = int(result.get("app_result_key", -1))
    if system_result_key == 0 and app_result_key == 0:
        msg = "开门成功"
    elif system_result_key == 7:
        msg = "系统错误"
    else:
        if "app_result_message_key" in result:
            msg = result["app_result_message_key"]
        else:
            msg = result.get("system_result_message_key", "未知错误")
    db.session.add(DoorLog(username=session["username"], door_id=door_id,
                           door_name=door_map.get(session["username"], {}).get(door_id), code=system_result_key, msg=msg))
    db.session.commit()
    return jsonify({"code": system_result_key, "msg": msg})


@app.route('/account', methods=['GET'])
@check_login
def account():
    return render_template(
        "account.html",
        door_logs=reversed(
            db.session.query(DoorLog).filter_by(username=session["username"]).order_by(DoorLog.time)[-50:]),
        username=session["username"],
        door_statistics=db.session.query(DoorLog, func.count(DoorLog.id))
        .filter_by(username=session["username"], code=0)
        .group_by(DoorLog.door_name).all()
    )
