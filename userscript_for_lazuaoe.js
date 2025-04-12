// ==UserScript==
// @name         rakou_bot parameter mapper for lazuaoe
// @namespace    http://tampermonkey.net/
// @version      2025-04
// @description  Mapping rakou_bot parameter to input form.
// @author       rakou1986
// @match        http://lazuaoe.php.xdomain.jp/rate/*
// @grant        none
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// ==/UserScript==

(function() {
    const $ = window.jQuery.noConflict(true);

    window.addEventListener("load", function () {
        var params = new URLSearchParams(window.location.search);
        var raw = params.get("rakou_bot_param_members");
        if (!raw) return;

        let members;
        try {
            members = JSON.parse(decodeURIComponent(raw));
        } catch (e) {
            console.error("Failed to parse rakou_bot_parameter:", e);
            return;
        }

        for (var i = 1; i < members.length+1; i++) {
            var name = members[i-1];
            $(`#kwp${i}`).find("input").val(name);
        }
    });
})();
