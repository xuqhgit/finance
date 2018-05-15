/**
 * Created by Administrator on 2017/4/6.
 */

/**
 * admin 通用提示窗口
 * @param msg
 * @returns
 */
var cAlert=function(msg,callback){
	//TODO 后期更改提示方式
	alert(msg);
	// window.wxc.xcConfirm(msg, window.wxc.xcConfirm.typeEnum.info,{onOk:function(){
	// 	if(callback)callback();
	// }});
};

var request = function(url,param,callback,settings){
	var rid = new Date().getTime()+""+Math.floor(Math.random()*10000);
	$("body").append("<div class='overlay' id='"+rid+"' ><div class='content'><div class='loader'></div></div></div>");

	$.ajax({
		  type: 'POST',
		  url: url,
		  data: param,
		  dataType: 'json',
		  traditional: true,
		  success: function(data, status){
			  $("#"+rid).remove();
			  if(status=='success'){
				  if(data.code==2)location.reload();
				  if(callback)callback(data);
			  }
			  else{
				 cAlert('请求失败：'+status);
			  }
		  },
		  error:function (XMLHttpRequest, textStatus, errorThrown){
			 $("#"+rid).remove();
			 cAlert("请求异常");
		  }
		});
};