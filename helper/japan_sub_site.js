animeList = document.getElementsByTagName('tr')
var index = 0;
for(var anime of animeList){
	anime.setAttribute('id', 'anime_'+index);
	
    var animeName = anime.getElementsByTagName('strong')[0].textContent;
	
	animeName = animeName.replace('-', ' ');
	var regex = /[!?@#$%^&*():;+-=~{}<>\_\[\]\|\\\"\'\,\.\/\`\₩]/g;
	animeName = animeName.replace(regex, "");

	var addTag = document.createElement("button");
	addTag.setAttribute('onclick', 'serachAnime('+index+',"' + animeName + '")');
	addTag.innerHTML = "Search";
	anime.append(addTag);
	
	index = index +1;
}

function serachAnime(index, animeName){
	temp = document.createElement('tr');
	temp2 = document.createElement('td');
	temp2.setAttribute('colspan', 4);
	temp.append(temp2);
	
	temp3 = document.createElement('iframe');
	temp3.setAttribute('src', 'https://123animehub.cc/search?keyword='+ animeName);
	temp3.setAttribute('width', '100%');
	temp3.setAttribute('height', 450);
	temp3.setAttribute('frameborder', 0);
	temp3.setAttribute('style', 'margin-bottom:20px;border:1px solid black');
	temp2.append(temp3);
	
	document.getElementById('anime_'+index).after(temp);
}
