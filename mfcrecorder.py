import datetime
import time
import os
import sys
import threading
import mfcauto
import classes
import webapp
from apscheduler.schedulers.background import BackgroundScheduler

app=webapp.app;

def job():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def modelLoop(config):  
    next_run = datetime.datetime.now()
    while True:
        if datetime.datetime.now() < next_run:
            time.sleep(0.1)
            continue
        print("another run {}".format(datetime.datetime.now()))
        next_run += datetime.timedelta(seconds=config.settings.interval)
        config.refresh()
        for uid, model in classes.models.get_online_models().items():
            if not config.does_model_pass_filter(model):
                continue
            classes.recording.start_recording(model.session, config)
            print("recording {}: {} ({} viewers) [{}]".format(model.name, model.session['uid'], model.session['rc'], model.tags))
        print('finished run')
        
if __name__ == 'mfcrecorder':
    #print("path-{}".format(sys.path[0]))
    config = classes.config.Config('./config.conf')
    #when config is edited at runtime and postprocessing is added, we cannot start it
    if config.settings.post_processing_command:
        classes.postprocessing.init_workers(config.settings.post_processing_thread_count)
    if config.settings.web_enabled:
        webapp.views.init_data(config)
#         app.run(host='0.0.0.0')
#         threading.Thread(
#             target=webapp.app.run,
#             kwargs={'host':'0.0.0.0', 'port':config.settings.port, 'threaded':'True', 'ssl_context':('certs/snakeoil.cert', 'certs/snakeoil.key')}
#         ).start()
    threading.Thread(
          target=modelLoop,
          args=[config]
      ).start()
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'cron', minute = '*/1')
    scheduler.start()
    file = open("/tmp/app-initialized",'w')
    

  

