from flask import Flask, render_template, session, redirect, url_for, flash, request, abort
import datetime
import os
import provider
import patient
import center
import utils

app = Flask(__name__, template_folder="../client/templates", static_folder='../client/static')
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = datetime.timedelta(hours=5)


def check_login():
    if 'email' not in session:
        return False
    return True


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', succeed=True)
    else:
        email = request.form["email"]
        password = request.form["password"]
        mode = request.form["role"]
        if mode == "provider":
            pvd = provider.Provider(email)
            if pvd.authenticater(password):
                session['email'] = email
                session['role'] = mode
                return redirect('/provider_profile/' + utils.quote(session['email']))
            else:
                return render_template('login.html',succeed=False)
        else:
            pt = patient.Patient(email)
            if pt.authenticater(password):
                session['email'] = email
                session['role'] = mode
                return redirect(url_for('index'))
            else:
                return render_template('login.html',succeed=False)


@app.route('/logout')
def logout():
    del session['email']
    del session['role']
    return render_template('login.html')


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if not check_login():
        return redirect(url_for('login'))
    if session['role'] != 'patient':
        return redirect('/provider_profile/' + utils.quote(session['email']))
    pt = patient.Patient(session['email'])
    center_v = ""
    provider_v = ""
    service_v = ""

    if request.method == "GET":
        results = pt.search(center=center_v, provider=provider_v, service=service_v)
        for res in results:
            pvd = provider.Provider(res['provider_email'])
            ct = center.Center(res['health_centre_name'])
            res['center_rate'] = ct.get_rate()
            res['provider_rate'] = pvd.get_rate()
            res['health_centre_name_quote'] = utils.quote(res['health_centre_name'])
            res['provider_email_quote'] = utils.quote(res['provider_email'])
        return render_template('index.html', patient_email=session['email'], result_list=results)
    
    center_v = request.form["center"]
    provider_v = request.form["provider"]
    service_v = request.form["service"]
    results = pt.search(center=center_v, provider=provider_v, service=service_v)
    for res in results:
        pvd = provider.Provider(res['provider_email'])
        ct = center.Center(res['health_centre_name'])
        res['center_rate'] = ct.get_rate()
        res['provider_rate'] = pvd.get_rate()
        res['health_centre_name_quote'] = utils.quote(res['health_centre_name'])
        res['provider_email_quote'] = utils.quote(res['provider_email'])
    return render_template('index.html', patient_email=session['email'], result_list=results)


@app.route('/patient_profile/<email>')
def patient_profile(email):
    email = utils.unquote(email)
    if not check_login():
        return redirect(url_for('login'))
    pt = patient.Patient(email)
    book_history = pt.query_book()
    for item in book_history:
        item['provider_email_quote'] = utils.quote(item['provider_email']) 
        item['center_name_quote'] = utils.quote(item['center_name']) 
    if session['role'] == 'patient':
        return render_template('patient_profile.html', patient_email=email, book_history=book_history, patient_mode=True)
    else:
        return render_template('patient_profile.html', patient_email=email, book_history=book_history, patient_mode=False)

@app.route('/provider_profile/<email>', methods=['GET', 'POST'])
def provider_profile(email):
    email = utils.unquote(email)
    if not check_login():
        return redirect(url_for('login'))
    pvd = provider.Provider(email)
    info = pvd.info()
    ptype = info['provider_type']
    rate = pvd.get_rate()
    centres = pvd.list_centers()

    for item in centres:
        item['qs'] = utils.gen_query_string(
            {'center': item['health_centre_name'], 'provider': item['provider_email']})
        item['health_centre_name_quote'] = utils.quote(
            item['health_centre_name'])
    if session['role'] == 'patient':
        if request.method == 'GET':
            return render_template('provider_profile.html', provider_email_quote=utils.quote(item['provider_email']),success=False, patient_email=session['email'], patient_email_quote=utils.quote(session['email']), provider_email=email, provider_type=ptype, provider_rate=rate, center_list=centres, patient_mode=True)
        else:
            new_rate = request.form["rate"]
            flag=pvd.set_rate(session['email'], new_rate)
            return render_template('provider_profile.html', provider_email_quote=utils.quote(item['provider_email']), success=flag, provider_email=email, provider_type=ptype, provider_rate=new_rate, center_list=centres, patient_mode=True)
    elif session['email'] == email:
        return render_template('provider_profile.html', provider_email=email, provider_type=ptype, provider_rate=rate, center_list=centres, patient_mode=False)
    else:
        abort(401)


@app.route('/center_profile/<name>', methods=['GET', 'POST'])
def center_profile(name):
    name = utils.unquote(name)
    pmode = True if session['role'] == 'patient' else False
    if not check_login():
        return redirect(url_for('login'))
    ct = center.Center(name)
    info = ct.info()
    pvd_list = ct.list_providers()
    for pvd in pvd_list:
        pvd['provider_email_quote'] = utils.quote(pvd['provider_email'])
        pvd['qs'] = utils.gen_query_string({'center': name, 'provider': pvd['provider_email'], 'time':pvd['provider_time']})
    if request.method == 'GET':
        return render_template('center_profile.html', patient_mode=pmode, success=False, center_name_quote=utils.quote(info['name']),center=info, center_rate=ct.get_rate(), email_quote=utils.quote(session['email']), email=session['email'], provider_list=pvd_list)
    else:
        rate = request.form["rate"]
        patient = session["email"]
        ct.set_rate(patient, rate)
        return render_template('center_profile.html', patient_mode=pmode, success=True, center_name_quote=utils.quote(info['name']),center=info, center_rate=ct.get_rate(), email_quote=utils.quote(session['email']), email=session['email'], provider_list=pvd_list)


@app.route('/history')
def history():
    if not check_login():
        return redirect(url_for('login'))
    pvd = provider.Provider(session['email'])
    info = pvd.info()
    email = session['email']
    email_q = utils.quote(session['email'])

    history_list = pvd.book_history()
    for item in history_list:
        item['center_name_quote'] = utils.quote(item['center_name'])
        item['patient_email_quote'] = utils.quote(item['patient_email'])
        item['qs'] = utils.gen_query_string({'provider':session['email'],'center':item['center_name'],'patient': item['patient_email'], 'time':item['service_time'], 'comment':item['comment']})
    return render_template('history.html', provider_email=email, provider_email_quote=email_q, provider_type=info['provider_type'], history_list=history_list)


@app.route('/consult', methods=['GET', 'POST'])
def consult_patient():
    qs = request.query_string
    query_info = utils.parse_query_string(qs)
    if not check_login():
        return redirect(url_for('login'))
    pvd = provider.Provider(session['email'])

    email = session['email']
    email_q = utils.quote(session['email'])

    if request.method == 'GET':
        return render_template('consultation.html', qs=qs, provider_email=email, provider_email_quote=email_q, patient=query_info, consult_list=pvd.query_consult(query_info['patient']))
    else:
        note = request.form["note"]
        mp = request.form["medication-prescribed"]
        pvd.consult(query_info['patient'],
                    query_info['center'], query_info['time'], note, mp)
        return render_template('consultation.html', qs=qs, provider_email=email, provider_email_quote=email_q, patient=query_info, consult_list=pvd.query_consult(query_info['patient']))


@app.route('/book', methods=['GET', 'POST'])
def book():
    tp = [str(i).zfill(2) + ":" + str(j).zfill(2)
          for i in range(24) for j in [0, 30]]
    if not check_login():
        return redirect(url_for('login'))
    if request.method == 'GET':
        qs = request.query_string
        query_info = utils.parse_query_string(qs)
        query_info['patient'] = session['email']
        return render_template('make_appointment.html', qs=qs,service_time=query_info['time'],patient_email_quote=utils.quote(query_info['patient']), patient_email=query_info['patient'], center_name=query_info['center'], provider_email=query_info['provider'],  success=False, tp=tp)
    else:
        begin = request.form["begin-time"]
        end = request.form["end-time"]
        comment = request.form["comment"]
        provider = request.form["provider"]
        center = request.form["center"]
        pt = patient.Patient(session['email'])
        flag = pt.book(provider, center, begin, end, comment)
        qs = request.query_string
        query_info = utils.parse_query_string(qs)
        query_info['patient'] = session['email']
        return render_template('make_appointment.html', qs=qs,service_time=query_info['time'],patient_email_quote=utils.quote(query_info['patient']), patient_email=query_info['patient'], center_name=query_info['center'], provider_email=query_info['provider'], success=flag, tp=tp)


def listen(port):
    app.run(debug=True, port=port)
