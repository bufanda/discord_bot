""" hello world template """
def hello_world(name, cfg) -> str:
    """ hello world """
    html = f"<html><head></head><body><h1>Hello {name}!</h1>"
    html += f"<p>Version: {cfg.version}<br>VCS Ref: {cfg.vcs_ref}"
    html += f"<br>VCS Tag: {cfg.vcs_tag}</p>"
    html += "<p><a href='http://127.0.0.1:8000/config'>Config Information</a></p>"
    html += "</body></html>"

    return html
