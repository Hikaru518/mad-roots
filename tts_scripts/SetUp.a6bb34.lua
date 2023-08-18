MARKET_DECK = Global.getVar('MARKET_DECK')

SEED_DECK = Global.getVar('SEED_DECK')
SEED_START_COOD_0 = Global.getVar('SEED_START_COOD_0')
SEED_START_COOD_1 = Global.getVar('SEED_START_COOD_1')
SEED_START_COOD_2 = Global.getVar('SEED_START_COOD_2')
SEED_DIFF = Global.getVar('SEED_DIFF')

MARKET_CARD_DIFF = Global.getVar('MARKET_CARD_DIFF')

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
    local xPos = deckPos[1] + MARKET_CARD_DIFF
    for i = 1, 6 do
        deck.takeObject({ flip = true, position = { xPos, deckPos[2], deckPos[3] } })
        xPos = xPos + MARKET_CARD_DIFF
    end
end

function setUpSeed()
    local deck = getObjectFromGUID(SEED_DECK)
    deck.shuffle()

    local posDiff = SEED_DIFF
    local xPos = SEED_START_COOD_0
    local yPos = SEED_START_COOD_1
    local zPos = SEED_START_COOD_2

    for i = 1, 3 do
        xPos = SEED_START_COOD_0
        for j = 0, 2 do
            deck.takeObject({ flip = true, position = { xPos, yPos, zPos } })
            xPos = xPos + posDiff
        end
        zPos = zPos - posDiff
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

    -- place good soil
    for i = 1, 3 do
        local cood = cood_list[i]
        local xPos = ROOT_MAP_START_COOD_xPos + ROOT_MAP_DIFF * (cood[1] - 1)
        local yPos = ROOT_MAP_START_COOD_yPos - ROOT_MAP_DIFF * (cood[2] - 1)
        good_soil_deck.takeObject({ flip = true, position = { xPos, ROOT_MAP_START_COOD_zPos + 2, yPos } })
    end

    -- place bad soil
    for i = 4, 6 do
        local cood = cood_list[i]
        local xPos = ROOT_MAP_START_COOD_xPos + ROOT_MAP_DIFF * (cood[1] - 1)
        local yPos = ROOT_MAP_START_COOD_yPos - ROOT_MAP_DIFF * (cood[2] - 1)
        bad_soil_deck.takeObject({ flip = false, position = { xPos, ROOT_MAP_START_COOD_zPos + 2, yPos } })
    end

    -- place stonef
    for i = 7, 8 do
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