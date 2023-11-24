
window.setTimeout(function() { $(".alert").fadeTo(500, 0)}, 3500);


//用来制作PageDown
f = function() {
    if (typeof flask_pagedown_converter === "undefined")
        flask_pagedown_converter = Markdown.getSanitizingConverter().makeHtml;
    var textarea = document.getElementById("flask-pagedown-body");
    var preview = document.getElementById("flask-pagedown-body-preview");
    textarea.onkeyup = function() { preview.innerHTML = flask_pagedown_converter(textarea.value); }
    textarea.onkeyup.call(textarea);
}
if (document.readyState === 'complete')
    f();
else if (window.addEventListener)
    window.addEventListener("load", f, false);
else if (window.attachEvent)
    window.attachEvent("onload", f);
else
    f();


 //密码为八位及以上并且字母数字特殊字符三项都包括
var strongRegex = new RegExp("^(?=.{6,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g");
//密码为七位及以上并且字母、数字、特殊字符三项中有两项，强度是中等
var mediumRegex = new RegExp("^(?=.{6,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g");
var enoughRegex = new RegExp("(?=.{1,}).*", "g");

//密码的可见与隐藏、
        console.log($('#inputPwd'))
        var eyeFlag = false;
        $('.eye_icon').click(function(){
            if(!eyeFlag){
                $(this).css({'background-image': 'url(' + "../img/close_eye.png" + ')'});
                $('#inputPwd').attr('type','text');
            }else{
                $(this).css({'background-image': 'url(' + "../img/eye.png" + ')'});
                $('#inputPwd').attr('type','password')
            }
            eyeFlag = !eyeFlag;
        })

        //密码强度验证
        function passValidate(e) {
            var pwd = $.trim(e.value);
            if (pwd === '') {
                $('.pwdStrength').css({'display':'none'})
                $('.weak').css({
                    'background': 'rgb(238, 238, 238)'
                });
                $('.middle').css({
                    'background': 'rgb(238, 238, 238)'
                });
                $('.strong').css({
                    'background': 'rgb(238, 238, 238)'
                });
                $('.result').text('')
            } else {
                $('.pwdStrength').css({'display':'flex'})
                //密码为八位及以上并且字母数字特殊字符三项都包括
                var strongRegex = new RegExp("^(?=.{6,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g");
                //密码为七位及以上并且字母、数字、特殊字符三项中有两项，强度是中等
                var mediumRegex = new RegExp("^(?=.{6,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g");
                var enoughRegex = new RegExp("(?=.{1,}).*", "g");
                if (false == enoughRegex.test(pwd)) {
                } else if (strongRegex.test(pwd)) {
                    $('.strong').css({
                        'background': '#06ad06'
                    });
                    $('.result').text('Strong')
                } else if (mediumRegex.test(pwd)) {

                    $('.middle').css({
                        'background': '#FFC125'
                    });
                    $('.strong').css({
                        'background': 'rgb(238, 238, 238)'
                    });
                    $('.result').text('Middle')
                } else {

                    $('.weak').css({
                        'background': '#EE4000'
                    });
                    $('.middle').css({
                        'background': 'rgb(238, 238, 238)'
                    });
                    $('.strong').css({
                        'background': 'rgb(238, 238, 238)'
                    });
                    $('.result').text('Weak')
                }
            }
        }
