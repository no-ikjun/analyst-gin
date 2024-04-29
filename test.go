package main

import (
	"crypto/tls"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/analyst-gin/stockprice"
	"github.com/gin-gonic/gin"
	"github.com/go-resty/resty/v2"
	"github.com/joho/godotenv"
)

// Response and Item structs to hold API response data
type ApiResponse struct {
  Response ResponseBody `json:"response"`
}

type ResponseBody struct {
  Header  ResponseHeader `json:"header"`
  Body    ResponseBodyDetails `json:"body"`
}

type ResponseHeader struct {
  ResultCode string `json:"resultCode"`
  ResultMsg  string `json:"resultMsg"`
}

type ResponseBodyDetails struct {
  NumOfRows  int    `json:"numOfRows"`
  PageNo     int    `json:"pageNo"`
  TotalCount int    `json:"totalCount"`
  Items      ItemsWrapper `json:"items"`
}

type ItemsWrapper struct {
  Item []StockItem `json:"item"`
}

type StockItem struct {
  BasDt        string `json:"basDt"`
  SrtnCd       string `json:"srtnCd"`
  IsinCd       string `json:"isinCd"`
  ItmsNm       string `json:"itmsNm"`
  MrktCtg      string `json:"mrktCtg"`
  Clpr         string `json:"clpr"`
  Vs           string `json:"vs"`
  FltRt        string `json:"fltRt"`
  Mkp          string `json:"mkp"`
  Hipr         string `json:"hipr"`
  Lopr         string `json:"lopr"`
  Trqu         string `json:"trqu"`
  TrPrc        string `json:"trPrc"`
  LstgStCnt    string `json:"lstgStCnt"`
  MrktTotAmt   string `json:"mrktTotAmt"`
}

func getStockPrice(c *gin.Context) {
  client := resty.New()
  client.SetTLSClientConfig(&tls.Config{
    MinVersion: tls.VersionTLS12,
    // InsecureSkipVerify: true, // 이 옵션은 보안에 위험하므로 신중히 사용해야 합니다.
})
  client.SetRetryCount(3).SetRetryWaitTime(8).SetRetryMaxWaitTime(8)
  client.SetTimeout(10 * time.Second)
  client.SetDebug(true)

  env_err := godotenv.Load(".env")
  if env_err != nil {
    log.Printf("Failed to load .env file: %s", env_err)
    c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to load .env file"})
    return
  }
  
  serviceKey := os.Getenv("SERVICE_KEY")
  url := "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
  url += "?serviceKey=" + serviceKey
  // url += "&numOfRows=1&pageNo=1&resultType=json"

  resp, _ := client.R().
    SetQueryParam("numOfRows", "10").
    SetQueryParam("pageNo", "1").
    SetQueryParam("resultType", "json").
    Get(url)

  
c.Data(resp.StatusCode(), "application/json", resp.Body())
}

func main() {
  r := gin.Default()
  stockprice.GetStockPrice()
  r.GET("/stockprice", getStockPrice)
  r.GET("/ping", func(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{
      "message": "pong",
    })
  })
  r.Run(":8080")
}