$(document).ready(function(){
	
   var subtask_form_id ;
	
   $('#popupDatepicker').datepick();
   $('#id_deadline').datepick({ altFormat: 'dd-mm-yy' });
   $('#id_requirement_date').datepick({ altFormat: 'dd-mm-yy' });


$("#expand").click(function(){

    $('#contacts ul > li')
	.find('ul')
	.show(40);

    });
    
$("li.active").hover( function() {
$(this).css('background-color' , '#EEEEEE');

},
 function() {
$(this).css('background-color' , '#FFFFFF');

}
);
$("#collapse").click(function(){

    $('#contacts ul > li')
	.find('ul')
	.hide(100);

    });



    $('#contacts ul > li')
	.find('ul:first')
	.stop(true, true)
	.slideToggle();

    $('#contacts ul > li ul')
	.click(function(e){
	    e.stopPropagation();
	})
	.filter(':not(:first)').hide();

    
    $('#contacts ul > li, #contacts ul > li > ul > li').click(function(){
	$(this)
	    .find('ul:first')
	    .stop(true, true)
	    .slideToggle();
    });
    
$("div.submit_botton_dissapear").hide();

// for the edit task template

  
function submit_dissapear_edittask()
{
alert("hey");
$("div.submit_button_dissapear").hide();

}
    $("div.show_subtask_form_class").hide();
    $(".image_subtask_slide").click(function (){

	subtask_form_id  ="div#show_"+$(this).attr('id');
	$(subtask_form_id).slideToggle(300);
	});
    
});



