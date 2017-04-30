for i in $(seq 20 20 9020); do wget "https://www.immigrationboards.com/british-citizenship/naturalisation-application-processing-timelines-only-t80616-$i.html"; done
python nparse.py
