MAP_BOUNDINGBOX_LEFT_UP = { 11.60, 1.16, 12.60 }
MAP_BOUNDINGBOX_RIGHT_DOWN = { 28.03, 1.16, -3.58 }

ROOT_DECK = Global.getVar('ROOT_DECK')
VISIBLE_ROOT_DECK = Global.getVar('VISIBLE_ROOT_DECK')

NORMAL_ROOT_TAG = Global.getVar('NORMAL_ROOT_TAG')
VISIBLE_ROOT_TAG = Global.getVar('VISIBLE_ROOT_TAG')

function is_in_map(object)
    pos = object.getPosition()
    if (pos.x > MAP_BOUNDINGBOX_LEFT_UP[1] and
            pos.x < MAP_BOUNDINGBOX_RIGHT_DOWN[1] and
            pos.z < MAP_BOUNDINGBOX_LEFT_UP[3] and
            pos.z > MAP_BOUNDINGBOX_RIGHT_DOWN[3])
    then
        return true
    else
        return false
    end
end

function is_flipped(object)
    return object.getRotation().z > 90
end

function is_not_deck(object)
    return object.type ~= "Deck"
end

function clean_normal_roots()
    local normal_roots = getObjectsWithTag(NORMAL_ROOT_TAG)
    local root_deck = getObjectFromGUID(ROOT_DECK)
    for i = 1, #normal_roots do
        local object = normal_roots[i]
        if is_not_deck(object) then
            print(is_in_map(object))
        end

        if (
                is_not_deck(object) and
                is_in_map(object) and
                not is_flipped(normal_roots[i])
            ) then
            normal_roots[i].flip()
            normal_roots[i].setPosition(root_deck.getPosition())
        end
    end

    root_deck.shuffle()
end

function clean_visible_roots()
    local visible_roots = getObjectsWithTag(VISIBLE_ROOT_TAG)
    local root_deck = getObjectFromGUID(VISIBLE_ROOT_DECK)
    for i = 1, #visible_roots do
        local object = visible_roots[i]
        if is_not_deck(object) then
            print(is_in_map(object))
        end

        if (
                is_not_deck(object) and
                is_in_map(object)
            ) then
            if is_flipped(object) then
                object.flip()
            end
            object.setPosition(root_deck.getPosition())
        end
    end

    root_deck.shuffle()
end

function cleanRoots()
    clean_normal_roots()
    clean_visible_roots()
end