# add and view punches, edit flagged
# main py file is clock
from datetime import datetime, datetime, date, time
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import desc
import logging


from .. import db
from ..extra import  get_time_total
from ..models import Users, Punch
from .webforms import FlagNote

punch = Blueprint("punch", __name__,
                  template_folder='templates',
                  url_prefix='/punch')

def user_timenow():
    now = datetime.now()
    if current_user.time_format == 0:
        return now.strftime("%T") # 24 hour
    else:
        return now.strftime("%I:%M:%S %p") # 12 hour

@punch.post('/one')
@login_required
def onepunch():
    now:datetime = datetime.now()
    time_now:time = datetime.strptime(now.strftime("%H:%M:%S"), "%H:%M:%S").time()
    user_time:time = user_timenow()
    
    type = request.args.get('type', default='', type=str)
    edit_user = Users.query.get(current_user.id)
    if type == 'i' and current_user.last_clock: #punch in already punched in
        # flag current punch for review
        # add new punch and update user
        # ("in -> in")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.flag = 'y'
        edit_punch.flag_note = 'auto - clocked in while already marked as clocked in'
        new_punch = Punch(clock_date=date.today(), clock_in=time_now,
                          user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash(f'Clocked In - {user_time}')
        logging.info(f'{current_user.name} clocked in')
        
    if type == 'i' and not current_user.last_clock: ### punch in not punched in
        # add new punch and update user
        # ("out -> in")
        new_punch = Punch(clock_date=date.today(), clock_in=time_now, 
                          user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash(f'Clocked In - {user_time}')
        logging.info(f'{current_user.name} clocked in, error already clocked in')

    if type == 'o' and not current_user.last_clock: # punch out not punched in
        # add new punch out and clear user punch and flag for review
        # ("out -> out")
        new_punch = Punch(clock_date=date.today(), clock_out=time_now, 
                          flag='y', user_id=current_user.id,
                          flag_note='auto - clocked out while already marked as clocked out')
        db.session.add(new_punch)
        db.session.commit()
        flash(f'Clocked Out - {user_time}')
        logging.info(f'{current_user.name} clocked out')

    if type == 'o' and current_user.last_clock: ### punch out and punched in
        # edit punch and clear user punch
        # ("in -> out")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.clock_out = time_now
        edit_user.last_clock = None
        time_total = get_time_total(edit_punch.clock_in, edit_punch.clock_out)
        edit_punch.time_total = time_total
        edit_punch.flag = 'n' if time_total else 'y'
        db.session.commit()
        flash(f'Clocked Out - {user_time}')
        logging.info(f'{current_user.name} clocked out, error already clocked out')
    
    return redirect(url_for('clock.punch.punches'), code=307)

@punch.post('/show')
@login_required
def punches():
    return render_template('punch/punches.html',
                           last=current_user.last_punch)

@punch.post('/pull')
@login_required
def pullpunches():
    punches_master = Punch.query.where(Punch.user_id==current_user.id).order_by(desc(Punch.clock_date), desc(Punch.clock_in),desc(Punch.clock_out))
    punches = db.paginate(punches_master, page=1, per_page=current_user.last_punch, error_out=False)
    page_search = punches.next_num
    return render_template('punch/table.html',
                           punches=punches,
                           last=current_user.last_punch,
                           page_search=page_search)

@punch.post('pullmore')
@login_required
def pullpunchesshowmore():
    page_search = request.args.get('page_search', default='', type=int)
    punches_master = Punch.query.where(Punch.user_id==current_user.id).order_by(desc(Punch.clock_date), desc(Punch.clock_in),desc(Punch.clock_out))
    punches = db.paginate(punches_master, page=page_search, per_page=current_user.last_punch, error_out=False)
    page_search = punches.next_num
    return render_template('punch/row-build.html',
                           punches=punches,
                           page_search=page_search)

@punch.post('/flag')
@login_required
def punchflag():
    id = request.args.get('id', default='', type=int)
    flag = request.args.get('flag', default='flag', type=str)
    punch = Punch.query.get_or_404(id)
    punch.flag = 'n' if flag == 'unflag' else 'y'
    db.session.commit()
    return redirect(url_for('clock.punch.punchshowrow',
                            id=punch.id), code=307)


@punch.post('/noteshow')
@login_required
def punchnoteshow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    form = FlagNote()
    form.flag_note.default = punch.flag_note
    form.process()
    return render_template('punch/note.html',
                           form=form,
                           punch=punch)

@punch.post('/note')
@login_required
def punchnote():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    form = FlagNote()
    punch.flag_note = form.flag_note.data
    db.session.commit()
    return redirect(url_for('clock.punch.punchshowrow',
                            id=punch.id), code=307)

@punch.post('/showrow')
@login_required
def punchshowrow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    return render_template('punch/row.html',
                           punch=punch)
