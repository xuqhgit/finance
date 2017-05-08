function formatJson(intfId){
	var id = "#intf_resp_"+intfId;
	var jsonStr = $(id+" p").text();
	try{
		var jsonObj = $.parseJSON(jsonStr);
		$(id+" div").empty();
		$(id+" div").JSONView(jsonObj).show();
		$(id+" p").hide();
		return true;
	}catch(e){ 
		cAlert(e.name); //Å×³öÒì³£ 
	}
	return false;
}