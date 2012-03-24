# create message

curl http://127.0.0.1:5000/api/messages/create \
	-d apikey="HAD7LPACVVA4VAAARVX756UKKLCZVF9F" \
	-d blurb="blurrrb" \
	-d heading="heading" \
	-d body="this is the body" \
	-d level="info"

# {
#   "status": "ok"
# }



# get messages

curl http://127.0.0.1:5000/api/messages/get \
	-d apikey="HAD7LPACVVA4VAAARVX756UKKLCZVF9F"

# {
#   "status": "ok",
#   "messages": [
#     {
#       "body": "message",
#       "level": "info",
#       "created": "2012-02-29 06:05:48.014000",
#       "heading": "heading",
#       "id": "4f4dc03c4922900e26000002",
#       "blurb": "blurb"
#     },
#     {
#       "body": "",
#       "level": "info",
#       "created": "2012-03-06 19:39:16.850000",
#       "heading": "heading",
#       "id": "4f5667e449229023ce000000",
#       "blurb": "bll"
#     },
#     {
#       "body": "This is a body",
#       "level": "info",
#       "created": "2012-03-06 19:55:04.569000",
#       "heading": "heading",
#       "id": "4f566b9849229025eb000000",
#       "blurb": "bll"
#     }
#   ]
# }