# Clana Websockets Client Example

This is a small example implementation of a websockets client to subscribe to ledger transactions. 

To stream the full ledger from the beginning:
```
python watcher.py
```

To stream the transaction of an account address:
```
python watcher.py <account>
```

The method `_load_last_state_version` in `Watcher` can be used to load the 
state version of the last received and stored transaction from e.g. a database or disk
(depending whether and where you store and process transactions in `transaction_handler`). 

However, be careful: a stored state version is account dependent and
different accounts need to have their own stored state version!