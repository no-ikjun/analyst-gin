package stockprice

import (
	"crypto/tls"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/joho/godotenv"
)

func GetStockPrice() {
	envErr := godotenv.Load(".env")
	if envErr != nil {
		log.Printf("Error loading .env file")
	}

	serviceKey := os.Getenv("SERVICE_KEY")
	url := fmt.Sprintf("https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo?serviceKey=%s&numOfRows=5&pageNo=1&resultType=json", serviceKey)

	httpTransport := &http.Transport{
		TLSClientConfig: &tls.Config{
			MinVersion: tls.VersionTLS12, // TLS 1.2 이상 사용
			PreferServerCipherSuites: true,
		},
	}
	
	httpClient := &http.Client{
		Transport: httpTransport,
		Timeout:   10 * time.Second, // 10초 타임아웃
	}
	
	resp, err := httpClient.Get(url)
	if err != nil {
		fmt.Println("HTTP request failed:", err)
		return
	}
	defer resp.Body.Close()
	
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Failed to read response body:", err)
		return
	}

	fmt.Println("Received response:", string(body))
}