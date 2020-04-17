import json
from _operator import methodcaller

from google.protobuf import descriptor
from google.protobuf.json_format import _Printer, _IsWrapperMessage, _WKTJSONMETHODS, _IsMapEntry, SerializeToJsonError


def getjson(message, including_default_value_fields=False,
            preserving_proto_field_name=False,
            indent=2,
            sort_keys=False,
            use_integers_for_enums=False,
            descriptor_pool=None):
    try:
        message = message()
    except:
        pass
    try:
        ms = message.ListFields()
        if not ms:
            printer = _Printer(
                including_default_value_fields,
                preserving_proto_field_name,
                use_integers_for_enums,
                descriptor_pool)
            return printer.ToJsonString(message, indent, sort_keys)
    except:
        pass
    printer = Printer(
        including_default_value_fields,
        preserving_proto_field_name,
        use_integers_for_enums,
        descriptor_pool)
    return printer.ToJsonString(message, indent, sort_keys)




class Printer(_Printer):

    def ToJsonString(self, message, indent, sort_keys):
        js = self._MessageToJsonObject(message)
        return json.dumps(js, indent=indent, sort_keys=sort_keys)



    def _MessageToJsonObject(self, message):
        """Converts message to an object according to Proto3 JSON Specification."""
        try:
            message_descriptor = message.DESCRIPTOR
        except:
            message_descriptor = message
        full_name = message_descriptor.full_name
        if _IsWrapperMessage(message_descriptor):
            return self._WrapperMessageToJsonObject(message)
        if full_name in _WKTJSONMETHODS:
            return methodcaller(_WKTJSONMETHODS[full_name][0], message)(self)
        js = {}
        return self._RegularMessageToJsonObject(message, js)

    def _RegularMessageToJsonObject(self, message, js):
        """Converts normal message according to Proto3 JSON Specification."""
        try:
            fields = message.ListFields()
        except:
            fields = message
        try:
            # Serialize default value if including_default_value_fields is True.
            try:
                if self.including_default_value_fields:
                    message_descriptor = fields
                    for field in message_descriptor.fields:
                        # Singular message fields and oneof fields will not be affected.
                        if ((field.label != descriptor.FieldDescriptor.LABEL_REPEATED and
                             field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE) or
                                field.containing_oneof):
                            continue
                        if self.preserving_proto_field_name:
                            name = field.name
                        else:
                            name = field.json_name
                        if name in js:
                            # Skip the field which has been serailized already.
                            continue
                        if _IsMapEntry(field):
                            js[name] = {}
                        elif field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
                            js[name] = []
                        else:
                            js[name] = self._FieldToJsonObject(field, field.default_value)
            except Exception as e:
                print(fields)
                print(e)


        except ValueError as e:
            raise SerializeToJsonError(
                'Failed to serialize {0} field: {1}.'.format(field.name, e))

        return js