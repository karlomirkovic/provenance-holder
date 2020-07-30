from ed25519 import SigningKey
import config


def fill_dummy(provenance_holder, user):
    message = []
    # Fill a message with 3 provenance entries
    # (chorid, chorver, choriden, workid, workver, workiden, input, b'invokesig, output, b'execsig)
    message.append([0, 1.0, 10, 1, 1.15, 20, "20"])
    message.append([1, 1.1, 11, 2, 1.16, 21, "20"])
    message.append([0, 1.2, 12, 3, 1.17, 22, "20"])

    for entry in message:
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
        invoke_signature = private_key.sign(invoke, encoding='hex')
        entry.append(invoke_signature)
        entry.append("20")
        execute = str(invoke_signature) + entry[8]
        execute = bytes(execute, 'utf-8')
        execute_signature = private_key.sign(execute, encoding='hex')
        entry.append(execute_signature)

    provenance_holder.controller.record(message, provenance_holder.providers[0], user)
