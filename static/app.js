"use strict"

/** handles favoriteclick event by changing favorite icon and
 *  adding/removing favorite from db
 */
 async function favoriteClick(evt) {
  evt.preventDefault();
  let msgId = $(evt.target).closest('div').data('message-id');

  // if message is liked
  if (evt.target.className === "fa fa-star") {
    evt.target.className = "far fa-star";
    $(evt.target).attr("style", "color:black");
  } else {
    evt.target.className = "fa fa-star"
    $(evt.target).attr("style", "color:rgb(244, 244, 51)");
  }

  axios({url: `/messages/${msgId}/like`, method: "POST"});
}

$("#messages").on("click", ".fa-star", favoriteClick);
