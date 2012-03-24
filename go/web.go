package main

import (
	"fmt"
	"net/http"
	"image"
	"image/png"
	"os"
	"io"
	"time"
	"crypto/md5"
	"strings"
	//"strconv"
	"sync"
	"launchpad.net/mgo"
	"launchpad.net/mgo/bson"
)

const (
	defaultImageFile = "bird.png"
	lenPath = len("/hitme/")
)

var (
	defaultImage image.Image
	loadOnce sync.Once
)

type Apikey struct {
	Status int
	Name string
	Userid string
	Key string
	Accessed int
}

type Hit struct {
	Md5 string
	Minute int64
	Userid string
	Userstring string
}


// load reads the various PNG images from disk and stores them in their
// corresponding global variables.
func load() {
	fmt.Println("Loading (should be one time only)")
    defaultImage = loadPNG(defaultImageFile)
}

func hitme(w http.ResponseWriter, r *http.Request) {
	defer func() {
		if defaultImage != nil {
			w.Header().Set("Content-type", "image/png")
			png.Encode(w, defaultImage)
		}
	}()

	// Load the defaultImage into memory (one time)
	loadOnce.Do(load)

	// TODO get the key out of the query string
	key := "HAD7LPACVVA4VAAARVX756UKKLCZVF9F"

	// Get the users unique details
	ip := r.RemoteAddr // 127.0.0.1:1234
	ipno := strings.Split(ip, ":")[0] // 127.0.0.1
	userString := r.UserAgent() + "_IP_" + ipno

	// Create a md5 hash of the users details
	h := md5.New()
	io.WriteString(h, userString)
	md5String := fmt.Sprintf("%x", h.Sum(nil))

	fmt.Println("Running goroutine... ")
	// Insert the hit in a separate goroutine (we won't wait for this to finish) 
	go insertHit(key, md5String, userString)

	// Send back the default image (remember this is a GET for a image)
	if defaultImage != nil {
		w.Header().Set("Content-type", "image/png")
		png.Encode(w, defaultImage)
	}
}

func insertHit(key, md5String, userString string) {
	// Connect to mongo
	session, err := mgo.Dial("127.0.0.1")
	if err != nil {
		panic(err)
	}
	defer session.Close()

	// Check that the apikey is valid
	ca := session.DB("droidpush").C("apikeys")

	result := Apikey{}
	err = ca.Find(bson.M{"key": key}).One(&result)
	if err != nil {
		// This means the key is not valid!!
		panic(err)
	}

	// TODO Before we insert the hit we need to do either
	// 		1. Check to see if the md5 already exists
	//		OR 2. Do a Upsert
	//  		_, err := db.dbcollection.Upsert(
	// 			bson.M{​"_id": key}, bson.M{"$addToSet": bson.M{key:obj}}))

	// Lets check to see if the md5 exists for this minute
	thisMinute := getThisMinute()
	ch := session.DB("droidpush").C("hits")
	count, err := ch.Find(bson.M{"minute": thisMinute, "md5": md5String}).Count()
	if err != nil {
		panic(err)
	}

	if count >= 1 {
		// This user has already 'hit' this minute
		fmt.Println("HIT EXISTS... relax")
	}else{
		// We have a valid user who hasn't 'hit' this minute, so lets insert
		// the entry into 'hits'
		fmt.Println("Hit does not exist... ")
		err = ch.Insert(&Hit{md5String, thisMinute, result.Userid, userString})
		fmt.Println("Inserting hit... ")

		if err != nil {
			panic(err)
		}
	}
} 

func getThisMinute() int64 {
	t := time.Now()
	tu := t.Unix()
	return tu / 60
}

func loadPNG(filename string) image.Image {
	f, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()
	m, err := png.Decode(f)
	if err != nil {
		panic(err)
	}
	return m
}

// func debugme(w http.ResponseWriter, r *http.Request) {
// 	key := "HAD7LPACVVA4VAAARVX756UKKLCZVF9F"

// 	// Get the users unique details
// 	ip := r.RemoteAddr // 127.0.0.1:1234
// 	ipno := strings.Split(ip, ":")[0] // 127.0.0.1
// 	userString := r.UserAgent() + "_IP_" + ipno

// 	// Create a md5 hash of the users details
// 	h := md5.New()
// 	io.WriteString(h, userString)
// 	md5String := fmt.Sprintf("%x", h.Sum(nil))

// 	//fmt.Fprintf(w, "<b>User (user agent and ip):</b> %s<br/><b>md5:</b> %s", userString, md5String)

// 	insertHit(key, md5String, userString)
// }


func main() {
	fmt.Println("Main... ")
	http.HandleFunc("/hitme", hitme)
	http.ListenAndServe(":8080", nil)
}