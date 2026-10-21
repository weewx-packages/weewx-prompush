# Repair validation

Version 1.1.0. Original repository and revision are in ORIGIN.md.

* https://github.com/sulrich/weewx-prompush/pull/6: Replaced Requests 2.10.0 pin with >=2.32.5,<3; removed unrelated setup dependency; ported Python 3 and installer. HTTP receiver/parser tests preserve zero, omit missing values, honor skip and report HTTP failures.

Tests run under WeeWX 4.10.2/5.1.0 on Python 3.10 and WeeWX 5.5.2 on Python 3.14. Local receivers and isolated install directories avoid live station changes. The tests do not establish individual external account permissions.
