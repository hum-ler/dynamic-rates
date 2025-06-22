from types import MappingProxyType

CURRENCIES = MappingProxyType({
    "AUD": {
        "code": "AUD",
        "symbol": "$",
        "name": "Australian Dollar",
        "exchange-rate": 1.1665196,
        "precision": 2,
        "region-emoji": "🇦🇺"
    },
    "CZK": {
        "code": "CZK",
        "symbol": "Kč",
        "name": "Czech Koruna",
        "exchange-rate": 17.655846,
        "precision": 0,
        "region-emoji": "🇨🇿"
    },
    "EUR": {
        "code": "EUR",
        "symbol": "€",
        "name": "Euro",
        "exchange-rate": 0.70580126,
        "precision": 2,
        "region-emoji": "🇪🇺"
    },
    "GBP": {
        "code": "GBP",
        "symbol": "£",
        "name": "Pound Sterling",
        "exchange-rate": 0.58744582,
        "precision": 2,
        "region-emoji": "🇬🇧"
    },
    "JPY": {
        "code": "JPY",
        "symbol": "¥",
        "name": "Japanese Yen",
        "exchange-rate": 113.95138,
        "precision": 0,
        "region-emoji": "🇯🇵"
    },
    "KRW": {
        "code": "KRW",
        "symbol": "₩",
        "name": "South Korean Won",
        "exchange-rate": 1064.2057,
        "precision": 0,
        "region-emoji": "🇰🇷"
    },
    "MYR": {
        "code": "MYR",
        "symbol": "RM",
        "name": "Malaysian Ringgit",
        "exchange-rate": 3.2991793,
        "precision": 2,
        "region-emoji": "🇲🇾"
    },
    "SGD": {
        "code": "SGD",
        "symbol": "$",
        "name": "Singapore Dollar",
        "exchange-rate": 1.0,
        "precision": 2,
        "region-emoji": "🇸🇬"
    },
    "TWD": {
        "code": "TWD",
        "symbol": "$",
        "name": "New Taiwan Dollar",
        "exchange-rate": 23.016292,
        "precision": 2,
        "region-emoji": "🇹🇼"
    },
    "USD": {
        "code": "USD",
        "symbol": "$",
        "name": "United States Dollar",
        "exchange-rate": 0.74135876,
        "precision": 2,
        "region-emoji": "🇺🇸"
    }
})
