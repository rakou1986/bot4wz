// ==UserScript==
// @name         rakou_bot parameter mapper for warzone
// @namespace    http://tampermonkey.net/
// @version      2025-04
// @description  Mapping rakou_bot parameter to input form.
// @author       rakou1986
// @match        http://warzone.php.xdomain.jp/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

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

        // 異なる名前空間、<script>タグ内のvar UserDataをパースしてvar playersとする
        var scripts = document.querySelectorAll("script");
        for (let script of scripts) {
            var text = script.textContent;
            var match = text.match(/var\s+UserData\s*=\s*(\[[\s\S]*?\]);/);

            if (match) {
                try {
                    /* eslint no-eval: 0 */
                    var players = eval(match[1]);
                } catch (e) {
                    console.error("Failed to extract UserData", e);
                }
                break;
            }
        }
        // 人数
        if (2 <= members.length && members.length <= 8) {
            $(`#slcNoP option[value=${members.length}]`).prop("selected", true);
        }
        // 名前を入力、warzone名と一致が確認できたらフォームにプレイヤーID(uid)、ステータスOKをセットする
        for (var i = 1; i < members.length+1; i++) {
            var name = members[i-1];
            var tr = $(`#trSearchP${i}`);
            tr.find("input.UserNameSuggest").val(name);
            if ( !name.startsWith("**") ) {
                players.forEach(function(player){
                    if (player.label == name) {
                        tr.find("[name='uid']").val(player.uid);
                        tr.find("[name='status']").text("OK");
                    }
                });
            }
        }
    });
})();
