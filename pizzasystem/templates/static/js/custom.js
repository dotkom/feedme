
$(document).ready(function()
{
    $("#id_need_buddy").click(function()
    {
        if($("#id_need_buddy").is(':checked'))
        {
            $("#id_buddy").prop('disabled', true);
        }
    });
});

$(document).ready(function()
{

    $("#id_pizza").val("derp");
});
