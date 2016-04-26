<script type="text/javascript" src="jquery.min.js"></script>

$("#pure-table tr").toggle(function(){
    $(this).css("background-color",'blue")
},function(){
    $(this).css("background-color",'black')
});