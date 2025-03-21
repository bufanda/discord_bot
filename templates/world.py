
def hello_world(name, cfg) -> str:
    """ hello world """
    html = f"<html><head></head><body><h1>Hello {name}!</h1>"
    html += f"<br>Version: {cfg.version}<br>VCS Ref: {cfg.vcs_ref}"
    html += f"<br>VCS Tag: {cfg.vcs_tag}"
    html += "</body></html>"

    return html
