var csrftoken = $("[name=csrfmiddlewaretoken]").val();
$("#id_username").keyup(function(){
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
                          $("<small class='form-text text-muted username_error'>Логин свободен.</small>").insertAfter("#id_username");
                      }
                      else{
                          $(".username_error").remove();
                          $("<small class='form-text username_error' style='color: red;'>Логин занят.</small>").insertAfter("#id_username");
                      }
                  })
                  .fail(function(){
                      console.log("failed");
                  })
              }
              else{
                  $(".username_error").remove();
              }
          });