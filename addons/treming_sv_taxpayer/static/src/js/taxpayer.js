/* Queda pendiente para despues */
//Busco el elemento de radio cuyo valor sea company
$(function(){
	//Si el radio se halla marcado entonces debo establecer el valor del campo invisible is_company
	if($("input[type=radio][value='company']").is(':checked')){
		$("input[name='is_company'][type='checkbox']").prop( "checked", true );
		alert("Compañia se ha checkeado");
	}else{
		$("input[name='is_company'][type='checkbox']").prop( "checked", false );
		alert("Compañia se ha descheckeado");
	}
})