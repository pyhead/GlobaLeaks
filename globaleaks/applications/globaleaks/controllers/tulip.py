def index():
    import hashlib

    if form.accepts(request.vars, session):
        l = request.vars

        # Make the tulip work well
        leak_number = l.Receipt.replace(' ','')
        tulip_url = hashlib.sha256(leak_number).hexdigest()
        redirect("/tulip/" + tulip_url)

    form = SQLFORM.factory(Field('Receipt', requires=IS_NOT_EMPTY()))

    if not form:
        if form.accepts(request.vars, session):
            l = request.vars

            # Make the tulip work well
            leak_number = l.Receipt.replace(' ','')
            tulip_url = hashlib.sha256(leak_number).hexdigest()
            redirect("/tulip/" + tulip_url)
    else:
        redirect("/")

    return dict(form=None,tulip_url=None)


# this is called only in the Target context
def access_increment(tulip):

    if tulip.accesses_counter:
        new_count = int(tulip.accesses_counter) + 1
        db.tulip[tulip.target].update_record(accesses_counter=new_count)
    else:
        db.tulip[tulip.target].update_record(accesses_counter=1)

    db.commit()

    if int(tulip.allowed_accesses) != 0 and \
       int(tulip.accesses_counter) > int(tulip.allowed_accesses):
        return True
    else:
        return False

# http://games.adultswim.com/robot-unicorn-attack-twitchy-online-game.html 
def record_comment(comment_feedback, tulip):
    db.comment.insert(leak_id=tulip.get_leak().get_id(), commenter_id=tulip.get_target(), comment=comment_feedback)
    db.commit()
    
    if tulip.feedbacks_provided:
        new_count = int(tulip.feedbacks_provided) + 1
        db.tulip[tulip.id].update_record(feedbacks_provided=new_count)
    else:
        db.tulip[tulip.id].update_record(feedbacks_provided=1)
    response.flash = "recorded comment"

def record_vote(vote_feedback, tulip):
    int_vote = int(vote_feedback)
    if int_vote <= 1 and int_vote >= (-1) and tulip.target != "0":
        tulip.set_vote(int_vote)
        response.flash = "Thanks for your contribution: actual Tulip pertinence rate: ", tulip.get_pertinentness()
    else:
        response.flash = "Invalid vote provided thru HTTP header manipulation: do you wanna work with us ?"

def status():
    tulip_url = request.args[0]

    try:
        tulip = Tulip(url=tulip_url)
    except:
        return dict(err=True)

    leak = tulip.get_leak()
    
    target = gl.get_target(tulip.target)

    if tulip.target == "0":
        whistleblower=True
        response.flash = "You are the Whistleblower"
        target_url = ''
    else:
        whistleblower=False
        target_url = "target/" + tulip.url
        response.flash = "You are the Target"

    if whistleblower == False:
    # the stats of the whistleblower stay in the tulip entry (its unique!)
        download_available = int(tulip.downloads_counter) < int(tulip.allowed_downloads)
        access_available = access_increment(tulip)
        counter_accesses = tulip.accesses_counter
        limit_counter = tulip.allowed_accesses
    else:
    # the stats of the whistleblower stay in the leak/material entry
        download_available = False
        if leak.whistleblower_access:
            new_count = int(leak.whistleblowing_access) + 1
            leak.whistleblower_access=new_count
        else:
            leak.whistleblower_counter=1

        counter_accesses = leak.whistleblower_access
        limit_counter = int("50") # settings.max_submitter_accesses
        access_available = True
    
    # check if the comment or a vote has been provided:
    if request.vars and request.vars.Comment:
        record_comment(request.vars.Comment, tulip)

    if request.vars and request.vars.Vote:
        record_vote(request.vars.Vote, tulip)  

    # OTHER CODE USAGE WAS:
    # form_comment = (Field('Comment', requires=IS_NOT_EMPTY()))
    # comment_input = SQLFORM.factory(*form_comment, table_name="form_comment")
    # if comment_input.accepts(request.vars, session):

    # configuration issue
    # *) if we want permit, in Tulip, to see how many download/clicks has been doing
    #    from the receiver, we need to pass the entire tulip list, because in fact
    #    the information about "counter_access" "downloaded_access" are different for each tulip.
    # or if we want not permit this information crossing, the interface simply has to stop in printing
    #    other receiver behaviour.
    # now is implement the extended version, but need to be selectable by the maintainer.
    tulipUsage = []
    flowers = db(db.tulip.leak_id == leak.get_id()).select()
    for singleTulip in flowers:
        if singleTulip.leak_id == tulip.get_id():
            tulipUsage.append(singleTulip)
        else:
            tulipUsage.append(singleTulip)
    # this else is obviously an unsolved bug, but at the moment 0 lines seem to match in leak_id
    
    feedbacks = []
    usersComment = db(db.comment.leak_id == leak.get_id()).select()
    for singleComment in usersComment:
        if singleComment.leak_id == leak.get_id():
            feedbacks.append(singleComment)         
            
    return dict(err=None,
            access_available=access_available,
            download_available=download_available,
            whistleblower=whistleblower,
            tulip_url=tulip_url,
            leak_id=leak.id,
            leak_title=leak.title,
            leak_tags=leak.tags,
            leak_desc=leak.desc,
            leak_material=leak.material,
            tulip_accesses=counter_accesses,
            tulip_allowed_accesses=limit_counter,
            tulip_download=tulip.downloads_counter,
            tulip_allowed_download=tulip.allowed_downloads,
            tulipUsage=tulipUsage,
            feedbacks=feedbacks,
            feedbacks_n=tulip.get_feedbacks_provided(),
            pertinentness=tulip.get_pertinentness(),
            previous_vote=tulip.get_vote(),
            name=tulip.target,
            target_url=target_url,
            targets=gl.get_targets("ANY"),
            files=pickle.loads(leak.material.file))

def download_increment(t):

    if (int(t.downloads_counter) > int(t.allowed_downloads)):
        return False

    if t.downloads_counter:
        new_count = int(t.downloads_counter) + 1
        db.tulip[t.target].update_record(downloads_counter=new_count)
    else:
        db.tulip[t.target].update_record(downloads_counter=1)

    db.commit()
    return True

def download():
    import os

    tulip_url = request.args[0]

    try:
        t = Tulip(url=tulip_url)
    except:
        redirect("/tulip/" + tulip_url);

    target = gl.get_target(t.target)

    if(download_increment(t)):
        redirect("/tulip/" + tulip_url);

    leak = t.get_leak()

    response.headers['Content-Type'] = "application/octet"
    response.headers['Content-Disposition'] = 'attachment; filename="' + \
                                              tulip_url + '.zip"'
    # XXX to make proper handlers to manage the fetch of dirname
    return response.stream(open(os.path.join(request.folder, 'material/',
                           db(db.submission.leak_id==leak.id).select().first(
                           ).dirname + '.zip'),'rb'))
