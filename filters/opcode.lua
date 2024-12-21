-- Define un nuevo protocolo
local my_bluetooth_proto = Proto("MyBluetooth", "My Bluetooth Protocol")

-- Definición de los campos del protocolo
local f_byte2 = ProtoField.uint8("mybluetooth.byte2", "Byte 2", base.HEX)
local f_byte3 = ProtoField.uint8("mybluetooth.byte3", "Byte 3", base.HEX)

my_bluetooth_proto.fields = {f_byte2, f_byte3}

-- Función principal del dissector
function my_bluetooth_proto.dissector(buffer, pinfo, tree)
    -- Verifica que el paquete sea suficientemente largo
    if buffer:len() < 3 then
        return
    end

    -- Obtén los bytes 2 y 3
    local byte2 = buffer(1, 1):uint()
    local byte3 = buffer(2, 1):uint()

    -- Añade una descripción en la columna Info
    pinfo.cols.info:set(string.format("Bytes 2 and 3: %02X %02X", byte2, byte3))

    -- Añade un nuevo árbol al protocolo
    local subtree = tree:add(my_bluetooth_proto, buffer(), "My Bluetooth Protocol")
    subtree:add(f_byte2, buffer(1, 1))
    subtree:add(f_byte3, buffer(2, 1))
end

-- Registra el protocolo en el puerto deseado o como subdissector
local bluetooth_table = DissectorTable.get("btl2cap.psm")
bluetooth_table:add(0x0001, my_bluetooth_proto) -- Ajusta el PSM según sea necesario
