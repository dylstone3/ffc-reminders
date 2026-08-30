# Each entry: the exact cron schedule string maps to that class's info.
# Edit the "name" fields with your real class names whenever you're ready.

CLASSES = {
    "tuesday": {  # fires Sunday 6:45 PM CDT -> reminds about Tuesday's class
        "name": "Book Swim Lane for 5:30-6:30pm and Heated Vinyasa",
        "class_day": "Tuesday",
        "class_time": "6:45 PM",
    },
    "thursday": {  # fires Tuesday 5:45 PM CDT -> reminds about Thursday's class
        "name": "Book Swim Lane for 5:15-6:15pm and Molten Mat",
        "class_day": "Thursday",
        "class_time": "5:45 PM",
    },
    "friday": {  # fires Wednesday 5:30 PM CDT -> reminds about Friday's class
        "name": "Book Heated Vinyasa",
        "class_day": "Friday",
        "class_time": "5:30 PM",
    },
    "saturday": {  # fires Thursday 10:45 AM CDT -> reminds about Saturday's class
        "name": "Book Heated Yoga Sculpt",
        "class_day": "Saturday",
        "class_time": "10:45 AM",
    },
    "sunday": {  # fires Friday 8:00 AM CDT -> reminds about Sunday's class
        "name": "Book rooftop Vinyasa Yoga",
        "class_day": "Sunday",
        "class_time": "8:00 AM",
    },
}
