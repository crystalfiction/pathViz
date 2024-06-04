--@enable = true
--@module = true

-- define module name
local GLOBAL_KEY = 'logPaths'

-- import repeat
local repeatUtil = require("repeat-util")
-- define modId
local modId = "logPaths"
-- define filePrefix to pathViz/ data directory
local filePrefix = ""

-- assert enabled
enabled = enabled or false
function isEnabled()
    return enabled
end

local function get_paths()
    -- define final data array
    local data = {}

    -- loop through all citizens
    for _, v in ipairs(dfhack.units.getCitizens(true, true)) do
        -- check that the unit is a dwarf...
        if (v.race == 572) then
            -- define the new unit data struc
            local newUnit = {
                goal = v.path.goal,
                path = {
                    x = v.path.path.x,
                    y = v.path.path.y,
                    z = v.path.path.z
                }
            }

            -- if newUnit exists...
            if newUnit ~= nil then
                -- insert to final data array
                table.insert(data, newUnit)
            end
        end
    end

    -- return the final data array
    return data
end

-- Get the date of the world as a string
-- Format: "YYYYY-MM-DD"
local function get_world_date_str()
    local month = dfhack.world.ReadCurrentMonth() + 1 --days and months are 1-indexed
    local day = dfhack.world.ReadCurrentDay()
    local date_str = string.format('%05d-%02d-%02d', df.global.cur_year, month, day)
    return date_str
end

local function write_to_file(data)
    local filepath = string.gsub(get_world_date_str(), "-", "") .. ".txt"
    local logFile = io.open(filePrefix .. filepath, "w")
    local unitCount = 0

    if logFile ~= nil then
        for i, u in ipairs(data) do
            -- save unit-level features
            local unitId = tostring(i)
            local unitGoal = tostring(u.goal)

            -- loop through unit path vectors
            -- where n = length of unit.path vectors
            local vLen = #u.path.x
            if vLen > 1 then
                -- for each path vector
                for v = 1, vLen - 1, 1 do
                    local textRow = tostring(unitId) ..
                        "," ..
                        tostring(unitGoal) ..
                        "," ..
                        tostring(u.path.x[v]) .. "," .. tostring(u.path.y[v]) .. "," .. tostring(u.path.z[v]) .. "\n"
                    logFile:write(textRow)
                end
            end

            unitCount = unitCount + 1
        end
    end

    print('Logged ' .. unitCount .. ' dwarf paths...')
end

dfhack.onStateChange[GLOBAL_KEY] = function(sc)
    if sc == SC_MAP_UNLOADED then
        dfhack.run_command('disable', 'logPaths')

        -- ensure our mod doesn't try to enable itself when a different
        -- world is loaded where we are *not* active
        dfhack.onStateChange[GLOBAL_KEY] = nil

        return
    end

    if sc ~= SC_MAP_LOADED or df.global.gamemode ~= df.game_mode.DWARF then
        return
    end

    dfhack.run_command('enable', 'logPaths')
end

if dfhack_flags.module then
    return
end

if not dfhack_flags.enable then
    print(dfhack.script_help())
    print()

    local flag = 'disabled'
    if enabled then
        flag = 'enabled'
    end

    print('logPaths is currently ' .. flag)
    return
end

-- check if module enabled...
if dfhack_flags.enable_state then
    -- if module is enabled
    -- monitor dwarf positions every 1wk or 8400 ticks
    -- *called before setting enabled flag for immediate logging*
    repeatUtil.scheduleEvery(modId .. 'every 1wk', 8400, 'ticks', function()
        -- get the data
        local newData = get_paths()
        -- if data exists, write to file
        if newData then
            write_to_file(newData)
        end
    end)

    -- set enabled
    enabled = true
    -- update user
    print("Logging dwarf positions every 1 week...")
else
    -- if module is not enabled
    -- cancel script repeat
    repeatUtil.cancel(modId .. 'every 1wk')

    -- set enabled
    enabled = false
    -- update user
    print("Stopped logging dwarf positions")
end
