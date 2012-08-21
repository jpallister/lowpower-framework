import httplib, urllib
import sys

def notify(title, message):
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages",
      urllib.urlencode({
        "token": "qbzNZ5cGu03hW3BCzIk83XficMaLBE",
        "user": "KgCpNHcu0lb28bRqndwn92oXDjdIyy",
        "title" : title,
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: notify.py title message"

    title = sys.argv[1]
    message = sys.argv[2]
    notify(title, message)

