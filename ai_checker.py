import re



def check_config(config):

    problems = []


    if len(config) < 20:
        problems.append(
            "کانفیگ خیلی کوتاه است"
        )


    if "USER" not in config and "کاربر" not in config:
        problems.append(
            "اطلاعات کاربر وجود ندارد"
        )


    if problems:

        return {
            "status": "error",
            "problems": problems
        }


    return {
        "status": "ok",
        "message": "کانفیگ سالم است"
    }