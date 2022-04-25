from flask import Blueprint, jsonify
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from pywizlight import wizlight, PilotBuilder, discovery


bp = Blueprint("lights", __name__)

async def get_light_dto(light):
    ip = light.ip
    color_state = await get_light_color_state(light)
    return {
        ip,
        color_state
    }

async def get_light_color_state(light):
    state = await light.updateState()
    white_temp = state.get_colortemp()
    red, green, blue = state.get_rgb()
    
    return {
        white_temp,
        red,
        green,
        blue,
    }


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    # return render_template("light/index.html")
    pass


@bp.route("/lights", methods=["GET"])
async def get_bulbs():
    """Get lights."""
    print("\033[H\033[J", end="")


    bulbs = await discovery.discover_lights(broadcast_space="192.168.1.255")
    # lights_state_list = [await get_light_dto(bulb) for bulb in bulbs]

    state = await get_light_dto(bulbs[0])
    # return jsonify(lights_state_list)
    return "xd"

@bp.route("/<int:id>/update", methods=("GET", "POST"))
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
