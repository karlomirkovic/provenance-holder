from ed25519 import SigningKey


def fill_dummy(provenance_holder, user):
    # Fill a message with 8 entries
    # Execution (cid, cver, cide, wid, wver, wid, input, b'invokesig', output, b'execsig', entry_type)
    # Adaptation (name, type, identifier, version, change, b'signature', entry_type)
    message = [[0, 1.0, 10, 1, 1.15, 20, "20", 'execution'],
               [1, 1.1, 11, 2, 1.16, 21, "20", 'execution'],
               [0, 1.2, 12, 3, 1.17, 22, "20", 'execution'],
               [0, 1.3, 13, 4, 1.18, 23, "30", 'execution'],
               ['mod_0', 'add', 0, 1.0, '+20', 'adaptation'],
               ['mod_1', 'add', 1, 1.1, '+30', 'adaptation'],
               ['mod_2', 'sub', 2, 1.2, '-20', 'adaptation'],
               ['mod_3', 'sub', 3, 1.3, '+30', 'adaptation']]

    for entry in message:
        # The last piece of data is the entry type
        entry_type = entry[len(entry) - 1]
        if entry_type == 'execution':
            # Concatenate the data in order to create the invoke signature
            invoke = str(entry[0]) + \
                     str(entry[1]) + \
                     str(entry[2]) + \
                     str(entry[3]) + \
                     str(entry[4]) + \
                     str(entry[5]) + \
                     entry[6]
            invoke = bytes(invoke, 'utf-8')

            # Reconstruct the private key using the ed25519 constructor
            private_key = SigningKey(user.private_key_sk)

            # Sign the data and store it in the entry as a replacement to
            # the entry type as it is needed only at the end of the list
            invoke_signature = private_key.sign(invoke, encoding='hex')
            entry[7] = invoke_signature
            # Append more dummy data, concatenate, and sign to create the execute signature
            entry.append("20")
            execute = str(invoke_signature) + entry[8]
            execute = bytes(execute, 'utf-8')
            execute_signature = private_key.sign(execute, encoding='hex')
            entry.append(execute_signature)
            # Append the entry type at the end of the list once again as it was previously replaced
            entry.append(entry_type)
        elif entry_type == 'adaptation':
            # Concatenate the necessary data for signing
            sig_msg = entry[0] + str(entry[3]) + entry[4]
            sig_msg = bytes(sig_msg, 'utf-8')
            # Reconstruct the private key using the ed 25519 constructor
            private_key = SigningKey(user.private_key_sk)
            signature = private_key.sign(sig_msg, encoding='hex')
            entry[5] = signature
            entry.append(entry_type)

    provenance_holder.controller.record(message, provenance_holder.providers, user)
