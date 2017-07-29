
// Handlers
function sendChat() {
    $.post(chat_link, {text: $("#chattext").val(), name: $("#chatname").val()})
    $("#chattext").val("")
}
function setName() {
    $.cookie("name", $("#chatname").val())
}
function closeChat() {
    $.stream(chat_link).close()
}
function onEnter(event, action) {
    if (event.which==13) {
        action()
        event.returnValue=false
    }
}
function editorChange(editor, event) {
}

// Set up
var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: "ruby",
    theme: "dark",
    lineNumbers: true,
    matchBrackets: true,
    onChange: editorChange
});
$.get(file_path, function(file) { editor.setValue(file) })

$("#chatname").val($.cookie("name"))
$.stream.setup({enableXDR: true})
$.stream(chat_link, {
    type: "http",
    dataType: "html",
    close: function(close) {
        $("#chatstream").html("")
    },
    handleMessage: function(text, message) {
        var msg = $.trim(text.substring(message.index))
        $("#chatstream").append(msg.replace(/\n/g, "<br/>") + "<br/>")
        message.data = text
        message.index = text.length
        return false
    }
});
