MARKET_DECK = Global.getVar('MARKET_DECK')
SEED_DECK = Global.getVar('SEED_DECK')

ROOT_MAP_START_COOD_xPos = Global.getVar('ROOT_MAP_START_COOD_0')
ROOT_MAP_START_COOD_yPos = Global.getVar('ROOT_MAP_START_COOD_2')
ROOT_MAP_START_COOD_zPos = Global.getVar('ROOT_MAP_START_COOD_1')
ROOT_MAP_DIFF = Global.getVar('ROOT_MAP_DIFF')

GOOD_SOIL_DECK = Global.getVar('GOOD_SOIL_DECK')
BAD_SOIL_DECK = Global.getVar('BAD_SOIL_DECK')
STONE_BAG = Global.getVar('STONE_BAG')

math.randomseed(os.time())


function shuffle(array)
    -- fisher-yates
    local output = {}
    local random = math.random

    for index = 1, #array do
        local offset = index - 1
        local value = array[index]
        local randomIndex = offset * random()
        local flooredIndex = randomIndex - randomIndex % 1

        if flooredIndex == offset then
            output[#output + 1] = value
        else
            output[#output + 1] = output[flooredIndex + 1]
            output[flooredIndex + 1] = value
        end
    end

    return output
end


function setUpMarket()
    local deck = getObjectFromGUID(MARKET_DECK)
    deck.shuffle()

    local deckPos = deck.getPosition()
    local xPos = deckPos[1] + 5.3
    for i = 1, 7 do
        deck.takeObject({ flip = true, position = { xPos, deckPos[2], deckPos[3] } })
        xPos = xPos + 5.3
    end
end


function setUpSeed()
    local deck = getObjectFromGUID(SEED_DECK)
    deck.shuffle()

    local deckPos = deck.getPosition()
    local posDiff = 2.45
    local xPos = deckPos[1] + posDiff
    for i = 1, 3 do
        local yPos = deckPos[3]
        for j = 0, 2 do
            deck.takeObject({ flip = true, position = { xPos, deckPos[2], yPos } })
            yPos = yPos + posDiff
        end
        xPos = xPos + posDiff
    end
end


function getCartesianProduct(x_list, y_list)
    local result = {}

    for i = 1, #x_list do
        for j = 1, #y_list do
            table.insert(result, { x_list[i], y_list[j] })
        end
    end
    return result
end


function initMapSetting()
    local good_soil_deck = getObjectFromGUID(GOOD_SOIL_DECK)
    local bad_soil_deck = getObjectFromGUID(BAD_SOIL_DECK)
    local stone_bag = getObjectFromGUID(STONE_BAG)

    local row_list = { 2, 3, 4, 5, 6 }
    local col_list = { 2, 3, 4, 5, 6 }
    local cood_list = getCartesianProduct(row_list, col_list)

    cood_list = shuffle(cood_list)

    for i = 1, 3 do
        local cood = cood_list[i]
        local xPos = ROOT_MAP_START_COOD_xPos + ROOT_MAP_DIFF * (cood[1] - 1)
        local yPos = ROOT_MAP_START_COOD_yPos - ROOT_MAP_DIFF * (cood[2] - 1)
        good_soil_deck.takeObject({ flip = false, position = { xPos, ROOT_MAP_START_COOD_zPos + 2, yPos } })
    end

    for i = 4, 6 do
        local cood = cood_list[i]
        local xPos = ROOT_MAP_START_COOD_xPos + ROOT_MAP_DIFF * (cood[1] - 1)
        local yPos = ROOT_MAP_START_COOD_yPos - ROOT_MAP_DIFF * (cood[2] - 1)
        bad_soil_deck.takeObject({ flip = false, position = { xPos, ROOT_MAP_START_COOD_zPos + 2, yPos } })
    end

    for i = 7, 7 do
        local cood = cood_list[i]
        local xPos = ROOT_MAP_START_COOD_xPos + ROOT_MAP_DIFF * (cood[1] - 1)
        local yPos = ROOT_MAP_START_COOD_yPos - ROOT_MAP_DIFF * (cood[2] - 1)
        stone_bag.takeObject({ flip = false, position = { xPos, ROOT_MAP_START_COOD_zPos + 2, yPos } })
    end
end


function setUp()
    setUpMarket()
    setUpSeed()
    initMapSetting()
    -- destroyObject(self)
end
