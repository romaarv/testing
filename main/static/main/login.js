var csrftoken = $("[name=csrfmiddlewaretoken]").val();

$("#id_username").change(function(){
    var username=$(this).val();
    if(username!=""){
        $.ajax({
            url:'/check_username_exist/',
            type:'POST',
            headers:{"X-CSRFToken": csrftoken },
            data:{username:username}
        })
        .done(function(response){
            console.log(response);
            if(response==0){
                $(".username_error").remove();
                $("<small class='form-text username_error' style='color: red;'>Логин не существует.</small>").insertAfter("#id_username");
                $(".btn-primary").attr('disabled', true);
            }
            else{
                if(response==1){
                    $(".username_error").remove();
                    $("<small class='form-text text-muted username_error'>Логин существует.</small>").insertAfter("#id_username");
                    $(".btn-primary").attr('disabled', false);
                }
                if(response==2){
                    $(".username_error").remove();
                    $("<small class='form-text username_error' style='color: red;'>Логин не активирован пользователем. Не выполнена активация указанная в письме.</small>").insertAfter("#id_username");
                    $(".btn-primary").attr('disabled', true);
                    }
                if(response==3){
                    $(".username_error").remove();
                    $("<small class='form-text username_error' style='color: red;'>Логин отключен администратором сайта.</small>").insertAfter("#id_username");
                    $(".btn-primary").attr('disabled', true);
                    }
            }
        })
        .fail(function(){
            console.log("failed");
        })
        }
        else{
            $(".username_error").remove();
            $(".btn-primary").attr('disabled', true);
        }
    }
);