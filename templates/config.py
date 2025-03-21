""" config module """
from modules.configmanager import ConfigManager

def web_config_print(base_url= None) -> str:
    """ Print Configuration """
    head = "<html><head></head><body>"
    body_header = "<h1>Configuration</h1>"
    trail = "</body></html>"

    if base_url is not None:
        body_header += f'<p><a href="{base_url}">Back</a></p>'

    env_body = "<h2>Environment variables</h2>"
    env_body += "<p>"

    cfg = ConfigManager()

    for key, value in cfg.environment_variables.items():
        if isinstance(value, str):
            if "PASSWORD" not in key and "TOKEN" not in key:
                env_body += f"{key}: {value}<br>"
            else:
                env_body += f"{key}: REDACTED<br>"
        else:
            env_body += f"{key}: {value}<br>"

    env_body += "</p>"

    db_body = "<h2>Configuration in Database</h2>"
    db_body += "<p>"

    for key, value in cfg.config.items():
        db_body += f"{key}: {value}<br>"

    db_body += "</p>"

    return head + body_header + env_body + db_body + trail
