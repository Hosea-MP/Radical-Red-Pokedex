async function fetchData() {
	
	let request = new Request(`https://raw.githubusercontent.com/JwowSquared/Radical-Red-Pokedex/master/data.js`);
    let response = null;
    if (typeof caches !== "undefined") {
        const cache = await caches.open(version);
        
        response = await cache.match(request);
        if (!response) {
            response = await fetch(request);
            await cache.put(request, response);
        }
        response = await cache.match(request);
    }
    else
        response = await fetch(request);
    
    let data = await response.text();
    data = new Function("return " + data + ";")();
    
    species = data.species;
    moves = data.moves;
    abilities = data.abilities;
    items = data.items;
    areas = data.areas;
    tmMoves = data.tmMoves;
    tutorMoves = data.tutorMoves;
    trainers = data.trainers;
    natures = data.natures;
    eggGroups = data.eggGroups;
    types = data.types;
    splits = data.splits;
    evolutions = data.evolutions;
    scaledLevels = data.scaledLevels;
    capIDs = data.capIDs;
    sprites = data.sprites;
    
    loadingScreen.className = "hide";
    document.querySelector("main").className = "";
}

function initializeSpriteMapping(speciesData) {
    spriteIndexMap = new Map();
    let currentIndex = 0;
    
    Object.values(speciesData)
        .sort((a, b) => a.dexID - b.dexID || a.order - b.order)
        .forEach(pokemon => {
            if (!spriteIndexMap.has(pokemon.ID)) {
                spriteIndexMap.set(pokemon.ID, currentIndex++);
            }
        });

    console.log("Sprite mapping initialized with", spriteIndexMap.size, "entries");
}

async function onStartup() {
	
	await fetchData();

	initializeSpriteMapping(species);
	
	setupTables();
	
	setupFilters();
	
	if(Array.prototype.equals)
			console.warn("Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code.");
	// attach the .equals method to Array's prototype to call it on any array
	Array.prototype.equals = function (array) {
		// if the other array is a falsy value, return
		if (!array)
			return false;
		// if the argument is the same array, we can be sure the contents are same as well
		if(array === this)
			return true;
		// compare lengths - can save a lot of time 
		if (this.length != array.length)
			return false;
	
		for (var i = 0, l=this.length; i < l; i++) {
			// Check if we have nested arrays
			if (this[i] instanceof Array && array[i] instanceof Array) {
				// recurse into the nested arrays
				if (!this[i].equals(array[i]))
					return false;       
			}           
			else if (this[i] != array[i]) { 
				// Warning - two different object instances will never be equal: {x:20} != {x:20}
				return false;   
			}           
		}       
		return true;
	}
	// Hide method from for-in loops
	Object.defineProperty(Array.prototype, "equals", {enumerable: false});

	/* console.log("First species:", Object.values(species)[0]); Debug data structure for species
	console.log("First item:", Object.values(items)[0]); Debug data structure for items */

}

onStartup();